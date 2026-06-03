"""Windows cp949 콘솔에서도 한글/특수문자 출력되도록 stdout 재설정."""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, Exception):
    pass
