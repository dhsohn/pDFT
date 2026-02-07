import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


@dataclass(frozen=True)
class SmokeCommandDeps:
    default_solvent_map_path: str
    smoke_test_xyz: str
    get_smoke_runs_base_dir: Callable[[], str]
    create_run_directory: Callable[[str], str]
    prepare_smoke_test_suite: Callable[[Any], tuple[dict, Path, list[str], list[dict]]]
    run_smoke_test_watch: Callable[[Any], None]
    coerce_smoke_statuses: Callable[[str], int]
    prepare_smoke_test_run_dir: Callable[[str, str, dict, int], Path]
    infer_smoke_case_status: Callable[[Path], str | None]
    update_smoke_progress: Callable[[str, Path, str, str | None], None]
    smoke_progress_status: Callable[[str, Path], str | None]
    load_smoke_test_status: Callable[[Path], str | None]
    coerce_smoke_status_from_metadata: Callable[[Path], None]
    write_smoke_skip_metadata: Callable[[Path, dict, str, str | None], None]
    build_smoke_test_config: Callable[[dict, str, dict], dict]
    run_smoke_test_case: Callable[..., int]
    ensure_smoke_status_file: Callable[[Path, int | None], None]
    format_subprocess_returncode: Callable[[int | None], str]


def _should_skip_resumed_smoke_case(args, deps: SmokeCommandDeps, base_run_dir, run_dir):
    if not args.resume:
        return False
    inferred_status = deps.infer_smoke_case_status(run_dir)
    if inferred_status in ("completed", "skipped"):
        deps.update_smoke_progress(base_run_dir, run_dir, inferred_status, None)
        logging.info("Skipping completed smoke-test case: %s", run_dir)
        return True
    progress_status = deps.smoke_progress_status(base_run_dir, run_dir)
    if progress_status in ("completed", "skipped"):
        logging.info("Skipping completed smoke-test case: %s", run_dir)
        return True
    status = deps.load_smoke_test_status(run_dir)
    if status in ("completed", "skipped"):
        deps.update_smoke_progress(base_run_dir, run_dir, status, None)
        logging.info("Skipping completed smoke-test case: %s", run_dir)
        return True
    if status is None:
        deps.coerce_smoke_status_from_metadata(run_dir)
    return False


def _run_smoke_test_matrix(
    *, args, deps: SmokeCommandDeps, base_config, base_run_dir, xyz_path, solvent_map_path, modes, cases
):
    total_cases = len(modes) * len(cases)
    failures = []
    case_index = 1
    for overrides in cases:
        for mode in modes:
            run_dir = deps.prepare_smoke_test_run_dir(
                base_run_dir, mode, overrides, case_index
            )
            case_index += 1
            if _should_skip_resumed_smoke_case(args, deps, base_run_dir, run_dir):
                continue
            if overrides.get("skip"):
                deps.write_smoke_skip_metadata(
                    run_dir,
                    overrides,
                    mode,
                    overrides.get("skip_reason"),
                )
                deps.update_smoke_progress(base_run_dir, run_dir, "skipped", None)
                logging.warning(
                    "Skipping smoke-test case due to unsupported dispersion: %s",
                    run_dir,
                )
                continue
            deps.update_smoke_progress(base_run_dir, run_dir, "running", None)
            smoke_config = deps.build_smoke_test_config(base_config, mode, overrides)
            smoke_config_raw = json.dumps(smoke_config, indent=2, ensure_ascii=False)
            smoke_config_path = run_dir / "config_smoke_test.json"
            smoke_config_path.write_text(smoke_config_raw, encoding="utf-8")
            try:
                exit_code = deps.run_smoke_test_case(
                    args=args,
                    run_dir=run_dir,
                    xyz_path=xyz_path,
                    solvent_map_path=solvent_map_path,
                    smoke_config_path=smoke_config_path,
                    smoke_config_raw=smoke_config_raw,
                    smoke_config=smoke_config,
                )
                deps.ensure_smoke_status_file(run_dir, exit_code)
                if exit_code == 0:
                    deps.update_smoke_progress(base_run_dir, run_dir, "completed", None)
                if exit_code != 0:
                    raise RuntimeError(
                        "Smoke-test subprocess exited with code "
                        f"{deps.format_subprocess_returncode(exit_code)}."
                    )
            except Exception as error:
                deps.update_smoke_progress(base_run_dir, run_dir, "failed", str(error))
                failures.append(
                    {
                        "run_dir": str(run_dir),
                        "mode": mode,
                        "basis": overrides["basis"],
                        "xc": overrides["xc"],
                        "solvent": overrides["solvent"],
                        "solvent_model": overrides["solvent_model"],
                        "dispersion": overrides["dispersion"],
                        "error": str(error),
                    }
                )
                if args.stop_on_error:
                    print("Smoke test stopped on error.")
                    print(
                        "  {mode} {basis} {xc} {solvent_model}/{solvent} "
                        "{dispersion} -> {run_dir} ({error})".format(**failures[-1])
                    )
                    raise SystemExit(1) from error
                continue
    return failures, total_cases


def run_smoke_test_command(args, deps: SmokeCommandDeps):
    if args.watch:
        if args.resume and not args.run_dir:
            raise ValueError("--resume requires --run-dir for smoke-test.")
        deps.run_smoke_test_watch(args)
        return

    base_config, _config_path, modes, cases = deps.prepare_smoke_test_suite(args)
    solvent_map_path = base_config.get("solvent_map") or deps.default_solvent_map_path
    if args.resume and not args.run_dir:
        raise ValueError("--resume requires --run-dir for smoke-test.")

    base_run_dir = args.run_dir or deps.create_run_directory(
        deps.get_smoke_runs_base_dir()
    )
    base_run_dir = str(Path(base_run_dir).expanduser().resolve())
    os.makedirs(base_run_dir, exist_ok=True)
    xyz_path = Path(base_run_dir) / "smoke_test_water.xyz"
    xyz_path.write_text(deps.smoke_test_xyz, encoding="utf-8")
    logging.warning("Starting smoke-test resume scan in %s", base_run_dir)
    coerced = deps.coerce_smoke_statuses(base_run_dir)
    if coerced:
        logging.warning(
            "Filled %s missing smoke-test status files from metadata.",
            coerced,
        )
    else:
        logging.warning("No missing smoke-test status files detected.")

    failures, total_cases = _run_smoke_test_matrix(
        args=args,
        deps=deps,
        base_config=base_config,
        base_run_dir=base_run_dir,
        xyz_path=xyz_path,
        solvent_map_path=solvent_map_path,
        modes=modes,
        cases=cases,
    )
    if failures:
        print(
            "Smoke test completed with failures: "
            f"{len(failures)}/{total_cases}"
        )
        for failure in failures:
            print(
                "  {mode} {basis} {xc} {solvent_model}/{solvent} "
                "{dispersion} -> {run_dir} ({error})".format(**failure)
            )
        raise SystemExit(1)
    print(f"Smoke test completed: {base_run_dir} ({total_cases} cases)")

