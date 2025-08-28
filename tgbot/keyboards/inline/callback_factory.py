from aiogram.filters.callback_data import CallbackData


class CancelingCallbackData(CallbackData, prefix="canceling"):
    key: str


class SubscriptionCallbackData(CallbackData, prefix="subscription"):
    key: str


class ScenarioCallbackData(CallbackData, prefix=" scenario"):
    key: str


class ScenarioCallbackData_update(CallbackData, prefix=" scenario_update"):
    key: str
