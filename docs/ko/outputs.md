# 출력물

## 디렉터리 구조 (예시)

```text
runs/2026-01-03_100104/0147_optimization/
  metadata.json
  config_used.json
  log/run.log
  log/run_events.jsonl
  optimized.xyz
  frequency_result.json
  irc_result.json
  irc_profile.csv
  qcschema_result.json
  scan_result.json
  scan_result.csv
  scan/
  snapshots/
```

## 주요 파일

- `metadata.json`: 실행 메타데이터 (상태, 설정, 버전, 요약)
- `config_used.json`: 실제 사용된 설정
- `log/run.log`: 런타임 로그
- `log/run_events.jsonl`: 상태 전이 이벤트 로그
- `optimized.xyz`: 최적화 구조 결과
- `frequency_result.json`: 진동수 결과
- `irc_result.json`, `irc_profile.csv`: IRC 결과 및 프로파일
- `qcschema_result.json`: QCSchema 형식 출력
- `scan_result.json`, `scan_result.csv`: 스캔 결과
- `snapshots/`: 중간 스냅샷 (옵션)

모든 파일이 항상 생성되는 것은 아니며, 계산 모드에 따라 생성 범위가 달라집니다.
