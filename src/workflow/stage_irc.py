import csv
import json
import logging
import os
import time

from ase_backend import _run_ase_irc
from run_opt_metadata import format_xyz_comment, write_checkpoint, write_xyz_snapshot
from run_opt_resources import resolve_run_path
from .events import finalize_metadata
from .utils import _atoms_to_atom_spec, _evaluate_irc_profile


def run_irc_stage(stage_context, queue_update_fn):
    logging.info("Starting IRC calculation...")
    run_start = stage_context["run_start"]
    calculation_metadata = stage_context["metadata"]
    profiling_enabled = bool(stage_context.get("profiling_enabled"))
    mode_profiling = stage_context.get("mode_profiling")
    run_dir = stage_context["run_dir"]
    checkpoint_path = stage_context.get("checkpoint_path")
    resume_dir = stage_context.get("resume_dir")
    charge = stage_context.get("charge")
    spin = stage_context.get("spin")
    multiplicity = stage_context.get("multiplicity")

    snapshot_dir = resolve_run_path(run_dir, "snapshots")
    forward_steps_snapshot = resolve_run_path(
        run_dir, "snapshots/irc_forward_steps.xyz"
    )
    reverse_steps_snapshot = resolve_run_path(
        run_dir, "snapshots/irc_reverse_steps.xyz"
    )
    forward_last_snapshot = resolve_run_path(run_dir, "snapshots/irc_forward_last.xyz")
    reverse_last_snapshot = resolve_run_path(run_dir, "snapshots/irc_reverse_last.xyz")

    checkpoint_base = {}
    if checkpoint_path and os.path.exists(checkpoint_path):
        try:
            with open(checkpoint_path, "r", encoding="utf-8") as checkpoint_file:
                checkpoint_base = json.load(checkpoint_file)
        except (OSError, json.JSONDecodeError):
            checkpoint_base = {}

    profile_cache = []
    profile_keys = set()
    if resume_dir and checkpoint_base.get("irc_profile"):
        profile_cache = list(checkpoint_base.get("irc_profile", []))
        for entry in profile_cache:
            key = (entry.get("direction"), entry.get("step"))
            profile_keys.add(key)

    resume_state = None
    if resume_dir and checkpoint_base:
        resume_state = {
            "forward_completed": bool(checkpoint_base.get("irc_forward_completed")),
            "reverse_completed": bool(checkpoint_base.get("irc_reverse_completed")),
        }
        for direction in ("forward", "reverse"):
            step_key = f"irc_{direction}_step"
            xyz_key = f"irc_{direction}_last_xyz"
            step_value = checkpoint_base.get(step_key)
            xyz_value = checkpoint_base.get(xyz_key)
            if xyz_value:
                resolved = resolve_run_path(run_dir, xyz_value)
                if os.path.exists(resolved):
                    resume_state[direction] = {
                        "step": step_value,
                        "xyz": resolved,
                    }

    def _persist_checkpoint():
        if not checkpoint_path:
            return
        write_checkpoint(checkpoint_path, checkpoint_base)

    def _record_irc_step(direction, step_index, atoms, energy_ev, energy_hartree):
        atom_spec = _atoms_to_atom_spec(atoms)
        comment = format_xyz_comment(
            charge=charge,
            spin=spin,
            multiplicity=multiplicity,
            extra=f"step={step_index} direction={direction}",
        )
        steps_path = (
            forward_steps_snapshot if direction == "forward" else reverse_steps_snapshot
        )
        last_path = (
            forward_last_snapshot if direction == "forward" else reverse_last_snapshot
        )
        write_xyz_snapshot(steps_path, atom_spec, comment=comment, append=True)
        write_xyz_snapshot(last_path, atom_spec, comment=comment)
        checkpoint_base.update(
            {
                "last_stage": "irc",
                "last_step": step_index,
                "last_geometry": atom_spec,
                "last_geometry_xyz": last_path,
                "snapshot_dir": snapshot_dir,
                "irc_forward_steps_xyz": forward_steps_snapshot,
                "irc_reverse_steps_xyz": reverse_steps_snapshot,
                "irc_direction": direction,
                f"irc_{direction}_step": step_index,
                f"irc_{direction}_last_xyz": last_path,
            }
        )
        entry_key = (direction, step_index)
        if entry_key not in profile_keys:
            profile_keys.add(entry_key)
            profile_cache.append(
                {
                    "direction": direction,
                    "step": step_index,
                    "energy_ev": float(energy_ev),
                    "energy_hartree": float(energy_hartree),
                }
            )
        checkpoint_base["irc_profile"] = profile_cache
        _persist_checkpoint()

    def _mark_direction_complete(direction, last_step):
        checkpoint_base[f"irc_{direction}_completed"] = True
        if last_step is not None:
            checkpoint_base[f"irc_{direction}_step"] = last_step
        _persist_checkpoint()

    try:
        irc_result = _run_ase_irc(
            stage_context["input_xyz"],
            stage_context["run_dir"],
            stage_context["charge"],
            stage_context["spin"],
            stage_context["multiplicity"],
            stage_context["calc_basis"],
            stage_context["calc_xc"],
            stage_context["calc_scf_config"],
            stage_context["calc_solvent_model"],
            stage_context["calc_solvent_name"],
            stage_context["calc_eps"],
            stage_context["calc_dispersion_model"],
            stage_context["verbose"],
            stage_context["memory_mb"],
            stage_context["optimizer_ase_config"],
            stage_context["optimizer_mode"],
            stage_context["constraints"],
            stage_context.get("mode_hessian"),
            stage_context["irc_steps"],
            stage_context["irc_step_size"],
            stage_context["irc_force_threshold"],
            profiling_enabled=profiling_enabled,
            step_callback=_record_irc_step,
            direction_callback=_mark_direction_complete,
            resume_state=resume_state,
        )
        profile = profile_cache or irc_result.get("profile", [])
        irc_payload = {
            "status": "completed",
            "output_file": stage_context["irc_output_path"],
            "forward_xyz": irc_result.get("forward_xyz"),
            "reverse_xyz": irc_result.get("reverse_xyz"),
            "steps": stage_context["irc_steps"],
            "step_size": stage_context["irc_step_size"],
            "force_threshold": stage_context["irc_force_threshold"],
            "mode_eigenvalue": stage_context.get("mode_eigenvalue"),
            "profile": profile,
            "profile_csv_file": stage_context["irc_profile_csv_path"],
            "profiling": {
                "mode": mode_profiling,
                "irc": irc_result.get("profiling"),
            }
            if profiling_enabled
            else None,
        }
        irc_payload["assessment"] = _evaluate_irc_profile(irc_payload["profile"])
        with open(stage_context["irc_output_path"], "w", encoding="utf-8") as handle:
            json.dump(irc_payload, handle, indent=2)
        with open(
            stage_context["irc_profile_csv_path"], "w", encoding="utf-8", newline=""
        ) as handle:
            direction_assessment = (
                irc_payload.get("assessment", {})
                .get("details", {})
                .get("directions", {})
            )
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "direction",
                    "step",
                    "energy_ev",
                    "energy_hartree",
                    "direction_status",
                    "direction_endpoint_energy_ev",
                    "direction_min_energy_ev",
                    "direction_drop_from_ts_ev",
                    "direction_min_drop_from_ts_ev",
                    "direction_endpoint_near_min",
                ],
            )
            writer.writeheader()
            for entry in irc_payload["profile"]:
                direction_detail = direction_assessment.get(entry.get("direction"), {})
                writer.writerow(
                    {
                        "direction": entry.get("direction"),
                        "step": entry.get("step"),
                        "energy_ev": entry.get("energy_ev"),
                        "energy_hartree": entry.get("energy_hartree"),
                        "direction_status": direction_detail.get("status"),
                        "direction_endpoint_energy_ev": direction_detail.get(
                            "endpoint_energy_ev"
                        ),
                        "direction_min_energy_ev": direction_detail.get("min_energy_ev"),
                        "direction_drop_from_ts_ev": direction_detail.get(
                            "endpoint_drop_from_ts_ev"
                        ),
                        "direction_min_drop_from_ts_ev": direction_detail.get(
                            "min_drop_from_ts_ev"
                        ),
                        "direction_endpoint_near_min": direction_detail.get(
                            "endpoint_near_min"
                        ),
                    }
                )
        calculation_metadata["irc"] = irc_payload
        if profiling_enabled and irc_payload.get("profiling") is not None:
            calculation_metadata.setdefault("profiling", {})["irc"] = irc_payload.get(
                "profiling"
            )
        energy_summary = None
        if irc_payload["profile"]:
            energy_summary = {
                "start_energy_ev": irc_payload["profile"][0]["energy_ev"],
                "end_energy_ev": irc_payload["profile"][-1]["energy_ev"],
            }
        summary = {
            "elapsed_seconds": time.perf_counter() - run_start,
            "n_steps": len(irc_payload["profile"]),
            "final_energy": energy_summary["end_energy_ev"] if energy_summary else None,
            "opt_final_energy": None,
            "final_sp_energy": None,
            "final_sp_converged": None,
            "final_sp_cycles": None,
            "scf_converged": None,
            "opt_converged": None,
            "converged": True,
        }
        calculation_metadata["summary"] = summary
        calculation_metadata["summary"]["memory_limit_enforced"] = stage_context[
            "memory_limit_enforced"
        ]
        finalize_metadata(
            stage_context["run_metadata_path"],
            stage_context["event_log_path"],
            stage_context["run_id"],
            stage_context["run_dir"],
            calculation_metadata,
            status="completed",
            previous_status="running",
            queue_update_fn=queue_update_fn,
            exit_code=0,
        )
    except Exception as exc:
        logging.exception("IRC calculation failed.")
        finalize_metadata(
            stage_context["run_metadata_path"],
            stage_context["event_log_path"],
            stage_context["run_id"],
            stage_context["run_dir"],
            calculation_metadata,
            status="failed",
            previous_status="running",
            queue_update_fn=queue_update_fn,
            exit_code=1,
            details={"error": str(exc)},
            error=exc,
        )
        raise
