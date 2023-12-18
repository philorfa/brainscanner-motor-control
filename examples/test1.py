import os
import sys
from pathlib import Path

sys.path.append(os.path.join(Path.cwd(), "../src"))
try:
    from gui import MotorControlApp
except (Exception,):
    raise


app = MotorControlApp()
app.mainloop()
sys.exit()
