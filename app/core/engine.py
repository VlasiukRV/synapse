from app.actions.auth_act import AuthCheckAction
from app.actions.email_act import EmailAction
from app.actions.db_act import DbSaveAction


class SynapseEngine:
    def __init__(self):

        self._actions = {
            "email_send": EmailAction(),
            "db_save": DbSaveAction(),
            "auth_check": AuthCheckAction()
        }

    async def run_flow(self, flow_config: list, data: dict, context: dict):
        report = []
        for step in flow_config:
            action_key = step['action']
            action_params = {**step.get('params', {}), **context}
            is_critical = step.get('critical', False)

            if action_key in self._actions:
                action = self._actions[action_key]
                try:
                    result = await action.execute(data, action_params)
                    report.append({"action": action_key, "result": result, "status": "success"})
                except Exception as e:
                    report.append({"action": action_key, "error": str(e), "status": "failed"})
                    if is_critical:
                        raise e
        return report