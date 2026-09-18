import os
import tempfile

# 必须在导入 app.* 之前指定独立数据目录，app.db 在导入时固化 DB_PATH。
os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="ladderbill-test-"))
