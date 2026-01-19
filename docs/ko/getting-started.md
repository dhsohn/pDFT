# 설치 및 시작

## 설치

DFTFlow는 conda 채널로 배포됩니다.

```bash
conda create -n dftflow -c daehyupsohn -c conda-forge dftflow
conda activate dftflow
```

- `pip install dftflow`는 지원되지 않습니다.
- GUI는 별도 앱(`dftflow_gui`)으로 제공됩니다.

## 환경 점검

```bash
dftflow doctor
```

## 구성 파일

- 지원 형식: `.json`, `.yaml/.yml`, `.toml`
- 기본 이름: `run_config.json`

예시(`run_config.yaml`):

```yaml
calculation_mode: optimization
basis: def2-svp
xc: b3lyp
solvent: vacuum
optimizer:
  mode: minimum
scf:
  max_cycle: 200
single_point_enabled: true
frequency_enabled: true
```

## 첫 실행

```bash
dftflow run path/to/input.xyz --config run_config.yaml
```

## 결과 확인

```bash
dftflow status --recent 5
```

로그는 기본적으로 `log/run.log`에 기록됩니다.
