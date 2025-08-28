from aiogram.fsm.state import StatesGroup, State

class Scenario(StatesGroup):
    get_name = State()
    get_email = State()
    painter_choice = State()
    get_impressions = State()
    next = State()


    before_audio = State()
    audio_choice = State()          # для выбора аудио-трека
    feedback = State()

    post_audio_choice = State()     # для вопросов после аудио
    get_promocode = State()   
    choose_audio =State()
    after_audio = State()  
    after_audio_options = State()
    payment = State()
    enter_promo = State()
    finish = State()
     

class Subscription(StatesGroup):
    email = State()

class MainMenu(StatesGroup):
    get_impressions = State()
