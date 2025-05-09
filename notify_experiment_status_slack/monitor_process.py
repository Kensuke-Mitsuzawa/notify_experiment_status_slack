import  yaml
import  psutil
import  argparse
import pathlib
from slack_sdk.webhook import WebhookClient
from  logzero  import  logger
from time import sleep



def message_start(webhook, process_id: int, user_name: str = None, label: str = None):
    p_obj = psutil.Process(pid=process_id)
    with p_obj.oneshot():
        # p_name = p_obj.name()
        p_name = p_obj
        
    is_process_exist = psutil.pid_exists(process_id)
    user_name_code = '' if user_name is None else f'@{user_name} '
    
    message = user_name_code + f'Started to check process_id = {process_id} / process-name={p_name} / label = {label}'
    logger.info(message)
    if is_process_exist:
        response = webhook.send(text=message)
        assert response.status_code == 200
        assert response.body == "ok"
    else:
        logger.error(f'Process {process_id} does not exist.')
        raise Exception()


def message_monitor(webhook, process_id: int, user_name: str = None, label: str = None, p_name: str = None):
    is_process_exist = psutil.pid_exists(process_id)

    if is_process_exist:
        p_obj = psutil.Process(pid=process_id)
        with p_obj.oneshot():
            # p_name = p_obj.name()
            p_name = str(p_obj)    
    
        message = f'[Running] p_name={is_process_exist} process_name={p_name} label={label}'
        logger.info(message)
        response = webhook.send(text=message)
        assert response.status_code == 200
        assert response.body == "ok"
        return True, p_name
    else:
        user_name_code = '' if user_name is None else f'@{user_name} '
        message = user_name_code + f'[END] it has gone. process_name={process_id} process_name={p_name} label={label}'
        logger.error(message)
        response = webhook.send(text=message)
        assert response.status_code == 200
        assert response.body == "ok"
        
        raise Exception()
        


def main():
    opt = argparse.ArgumentParser()
    opt.add_argument('-p', '--process_id', required=True, type=int)
    opt.add_argument('-m', '--monitor_interval', required=False, type=int, default=30, help='minutes')
    opt.add_argument('-c', '--path_config_yaml', required=True, type=str)
    opt.add_argument('-l', '--label', required=False, type=str)
    opt.add_argument('-u', '--user_name', 
                     required=False, 
                     type=str,
                     default=None,
                     help='mention-to in Slack. It mentions the user when it starts and ends.')
    args = opt.parse_args()
    
    p_conf = pathlib.Path(args.path_config_yaml).absolute()
    assert p_conf.exists()
    with open(args.path_config_yaml) as f:
        conf = yaml.safe_load(f.read())

    URL_WEBHOOK = conf['SLACK_WEBHOOK']
    
    webhook = WebhookClient(URL_WEBHOOK)
    message_start(webhook, args.process_id, args.user_name, args.label)
    _process_name = ''
    while True:
        sleep(args.monitor_interval * 60)
        _is_status, _process_name = message_monitor(webhook, args.process_id, args.user_name, args.label, _process_name)
        

if __name__ == '__main__':
    main()

