"""Run the library's edge-tts tool (core/tts/tts_zh.py) with a TLS context that trusts SSL_CERT_FILE.
edge-tts pins certifi's bundle; behind a TLS-inspecting proxy that bundle lacks the proxy's CA.
usage (library root): .venv/bin/python <project>/tools/tts_ms.py lines.json out_dir [tts_zh.py options]
"""
import os, ssl, sys, runpy
import edge_tts.communicate as c
ca = os.environ.get('SSL_CERT_FILE')
if ca and os.path.exists(ca):
    c._SSL_CTX = ssl.create_default_context(cafile=ca)
lib = os.environ.get('LIB') or os.getcwd()
sys.argv = [os.path.join(lib, 'core/tts/tts_zh.py')] + sys.argv[1:]
runpy.run_path(sys.argv[0], run_name='__main__')
