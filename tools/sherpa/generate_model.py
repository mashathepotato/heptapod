
import re, os, sys, Sherpa

sherpa_base_dir = os.path.dirname(Sherpa.__file__)
sys.path.append(sherpa_base_dir)

sys.argv.append('--root_dir')
sys.argv.append(sherpa_base_dir+'/share/SHERPA-MC')
sys.argv.append('--install_dir')
if os.path.isdir(sherpa_base_dir+'/lib/SHERPA-MC'):
    sys.argv.append(sherpa_base_dir+'/lib/SHERPA-MC')
if os.path.isdir(sherpa_base_dir+'/lib64/SHERPA-MC'):
    sys.argv.append(sherpa_base_dir+'/lib64/SHERPA-MC')

from ufo_interface.parser import main
if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main(sys.argv[1:]))
