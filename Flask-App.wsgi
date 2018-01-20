import sys
import logging
logging.basicConfig(stream=sys.stderr)

from app import create_app
application = create_app('production')
application.secret_key = '}\x0e\xe9V\x88\xdc\xe5\xfa\xec={\t9\x92"\x11u\x1e\xfd\xea\xbd\xaa\x17\x97'