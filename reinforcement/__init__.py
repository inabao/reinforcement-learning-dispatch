from setting import *
if algorithm == "model":
    from .LearningBased import stateValueInit, stateValueSave, assess, reward2discount
else:
    from .tabular import stateValueInit, stateValueSave, assess, reward2discount