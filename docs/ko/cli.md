# CLI 레퍼런스

## run

```bash
dftflow run input.xyz --config run_config.yaml
```

주요 옵션:

- `--background`: 백그라운드 큐 실행
- `--profile`: SCF/gradient/Hessian 타이밍 기록
- `--resume <RUN_DIR>`: 기존 실행 재개
- `--force-resume`: 완료/실패 상태도 재개 허용
- `--queue-priority <N>`: 큐 우선순위
- `--queue-max-runtime <SEC>`: 큐 타임아웃
- `--scan-dimension ...`, `--scan-mode ...`, `--scan-grid ...`: CLI 스캔 오버라이드

## status

```bash
dftflow status

dftflow status --recent 5
```

## queue

```bash
dftflow queue status
dftflow queue cancel <RUN_ID>
dftflow queue retry <RUN_ID>
dftflow queue requeue-failed
dftflow queue prune --keep-days 30
dftflow queue archive
```

## validate-config

```bash
dftflow validate-config run_config.yaml
```

## doctor

```bash
dftflow doctor
```

## smoke-test

```bash
dftflow smoke-test --smoke-mode quick
```

## scan-point (고급)

`scan.executor: manifest`로 생성된 매니페스트를 사용해 포인트를 실행합니다.

```bash
dftflow scan-point --manifest path/to/scan_manifest.json --index 0
```
