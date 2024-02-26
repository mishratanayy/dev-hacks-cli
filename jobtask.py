from schrodinger.tasks import jobtasks
from schrodinger.infra import mmjob
from schrodinger.utils import qapplication
from schrodinger.utils import preferences
 
 
#pref_handler = preferences.Preferences(preferences.SHARED)
#pref_handler.set("jobcontrol/update_notify_count", 50000)
 
app = qapplication.get_application()
mmjob.timing_debug_on()
 
 
task = jobtasks.CmdJobTask(cmd_list=['testapp', '-t', '1','-PROJ',"/Users/mishra/delme/test_2.prj"])
task.start()
task.wait()

