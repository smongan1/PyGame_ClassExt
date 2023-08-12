
def safeRun(RUNNING_GAME, handlerConfigs):
    exec("""import pygame as pg""", globals())
    pg.font.init()
    pg.init()
    exec("""ind_to_letter = { getattr(pg,'K_' + x) : x for i,x in enumerate('abcdefghijklmnopqrstuvwxyz')}""", globals())
    exec("""letter_to_ind = { x : getattr(pg,'K_' + x) for i,x in enumerate('abcdefghijklmnopqrstuvwxyz')}""", globals())
    try:
        handle = RUNNING_GAME.GetGameHandle(**handlerConfigs)
    except:
        e = Exception("quiting")
        raise(e)
    finally:
        pg.quit()
    return handle
    # Run until the user asks to quit