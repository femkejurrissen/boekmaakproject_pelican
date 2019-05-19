from flask import Flask, send_file, request
from werkzeug.exceptions import abort
import subprocess
import settings
from datetime import datetime

app = Flask(__name__)

def pull ():
  args = ['git', 'pull']
  return subprocess.check_output(args, cwd=settings.repodir, stderr=subprocess.STDOUT).decode()

def generate ():
  args = [
    settings.pelican,
    '-o', settings.outputdir,
    '-s', settings.settings_file
  ]

  return subprocess.check_output(args, cwd=settings.sitedir, stderr=subprocess.STDOUT).decode()

@app.route('/deploy', methods=["GET", "POST"])
def deploy ():
  if settings.gitlab_token is None or request.headers.get('X-Gitlab-Token') == settings.gitlab_token:
    with open(settings.log_file, 'w') as f:
      f.write('{}\n\n'.format(datetime.now().isoformat(' ')))
      f.write('*** Pulling from remote ***\n')
      f.write(pull())
      f.write('\n\n*** Regenerating site ***\n')
      f.write(generate())
      f.close()

    return open(settings.log_file, 'r').read()
  else:
    abort(404)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5556, debug=True)