import os
from dataclasses import dataclass
@dataclass(frozen=True)
class Config:
    cortex_url: str = os.getenv('CORTEX_URL','http://127.0.0.1:7331').rstrip('/')
    username: str = os.getenv('CORTEX_USERNAME','admin')
    password: str = os.getenv('CORTEX_PASSWORD','')
    workspace: str = os.getenv('CORTEX_WORKSPACE','')
    vant_bin: str = os.getenv('VANT_BIN','vant')
    max_steps: int = int(os.getenv('BENCHMARK_MAX_STEPS','100'))
