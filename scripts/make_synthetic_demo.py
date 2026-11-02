"""GENERATES SYNTHETIC DATA FOR TESTING THE PROGRAM. Not real CAN observations."""
from pathlib import Path
import numpy as np
import pandas as pd

root = Path('data/synthetic/set_01')
splits = [
    'train_01', 'test_01_known_vehicle_known_attack',
    'test_02_unknown_vehicle_known_attack',
    'test_03_known_vehicle_unknown_attack',
    'test_04_unknown_vehicle_unknown_attack',
]
rng = np.random.default_rng(1337)
for si, split in enumerate(splits):
    folder = root / split
    folder.mkdir(parents=True, exist_ok=True)
    for capture in range(6 if si == 0 else 2):
        n = 500
        attacked = rng.random(n) < .22
        ids = rng.choice([0x100, 0x190, 0x200, 0x300], n)
        ids[attacked] = 0x001 if si % 2 == 0 else 0x777
        payload = [rng.bytes(8).hex().upper() if not x else 'FF00000000000000' for x in attacked]
        dat = pd.DataFrame({
            'timestamp': 1672531200 + np.arange(n)*.005 + capture*3,
            'arbitration_id': [f'{x:03X}' for x in ids],
            'data_field': payload, 'attack': attacked.astype(int),
        })
        # Match common published no-header CSV lines, with 4 fields.
        dat.to_csv(folder / f'capture_{capture:02d}.csv', index=False, header=False)
print(f'Wrote synthetic smoke-test data under {root}. NEVER report these results as thesis findings.')
