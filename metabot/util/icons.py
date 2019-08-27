"""Lists of topic-related icons."""

import re

GOOGLE_PATTERN = 'https://ssl.gstatic.com/calendar/images/eventillustrations/v1/img_%s_2x.jpg'
GOOGLE_TABLE = (
    # Language code: en
    ('new year', 'genericnewyear'),  # flag: 3
    ("new year's", 'genericnewyear'),  # flag: 3
    ('new years', 'genericnewyear'),  # flag: 3
    ('babyshower', 'babyshower'),  # flag: 2
    ('maternity', 'babyshower'),  # flag: 2
    ('baby shower', 'babyshower'),  # flag: 2
    ('jog', 'running'),  # flag: 2
    ('jogging', 'running'),  # flag: 2
    ('running', 'running'),  # flag: 2
    ('jogs', 'running'),  # flag: 2
    ('track and field', 'running'),  # flag: 2
    ('track & field', 'running'),  # flag: 2
    ('sprinting', 'running'),  # flag: 2
    ('book club', 'bookclub'),  # flag: 2
    ('reading', 'bookclub'),  # flag: 2
    ('thanksgiving', 'thanksgiving'),  # flag: 2
    ('date night', 'datenight'),  # flag: 3
    ('datenight', 'datenight'),  # flag: 3
    ('candlelight dinner', 'datenight'),  # flag: 3
    ('candle light dinner', 'datenight'),  # flag: 3
    ('romantic dinner', 'datenight'),  # flag: 3
    ('handicraft', 'handcraft'),  # flag: 2
    ('crochet', 'handcraft'),  # flag: 2
    ('knitting', 'handcraft'),  # flag: 2
    ('patchwork', 'handcraft'),  # flag: 2
    ('embroidery', 'handcraft'),  # flag: 2
    ('quilting', 'handcraft'),  # flag: 2
    ('sewing', 'handcraft'),  # flag: 2
    ('felting', 'handcraft'),  # flag: 2
    ('millinery', 'handcraft'),  # flag: 2
    ('cocktail', 'drinks'),  # flag: 2
    ('drinks', 'drinks'),  # flag: 2
    ('cocktails', 'drinks'),  # flag: 2
    ('stag night', 'drinks'),  # flag: 2
    ('hen night', 'drinks'),  # flag: 2
    ('bachelorette party', 'drinks'),  # flag: 2
    ('stag party', 'drinks'),  # flag: 2
    ('stag do', 'drinks'),  # flag: 2
    ('hen do', 'drinks'),  # flag: 2
    ('stag and doe', 'drinks'),  # flag: 2
    ('ladies night', 'drinks'),  # flag: 2
    ('wine night', 'drinks'),  # flag: 2
    ('wine bar', 'drinks'),  # flag: 2
    ('fridge repair', 'repair'),  # flag: 2
    ('handyman', 'repair'),  # flag: 2
    ('electrician', 'repair'),  # flag: 2
    ('plumber', 'repair'),  # flag: 2
    ('diy', 'repair'),  # flag: 2
    ('christmas', 'xmas'),  # flag: 3
    ('xmas', 'xmas'),  # flag: 3
    ('x-mas', 'xmas'),  # flag: 3
    ('boxing day', 'xmas'),  # flag: 3
    ('cooking', 'cooking'),  # flag: 3
    ('cook dinner', 'cooking'),  # flag: 3
    ('cook lunch', 'cooking'),  # flag: 3
    ('cook meal', 'cooking'),  # flag: 3
    ('prepare meal', 'cooking'),  # flag: 3
    ('prepare dinner', 'cooking'),  # flag: 3
    ('prepare lunch', 'cooking'),  # flag: 3
    ('make dinner', 'cooking'),  # flag: 3
    ('make lunch', 'cooking'),  # flag: 3
    ('kayaking', 'kayaking'),  # flag: 2
    ('canoeing', 'kayaking'),  # flag: 2
    ('canoe', 'kayaking'),  # flag: 2
    ('backtoschool', 'backtoschool'),  # flag: 2
    ('back to school', 'backtoschool'),  # flag: 2
    ('first school day', 'backtoschool'),  # flag: 2
    ('first day of school', 'backtoschool'),  # flag: 2
    ('back2school', 'backtoschool'),  # flag: 2
    ('back 2 school', 'backtoschool'),  # flag: 2
    ('equestrian', 'equestrian'),  # flag: 2
    ('dressage', 'equestrian'),  # flag: 2
    ('eventing', 'equestrian'),  # flag: 2
    ('horse riding', 'equestrian'),  # flag: 2
    ('horseriding', 'equestrian'),  # flag: 2
    ('santa claus', 'santa'),  # flag: 2
    ('father christmas', 'santa'),  # flag: 4
    ('wedding', 'wedding'),  # flag: 2
    ('wedding eve', 'wedding'),  # flag: 2
    ('wedding-eve party', 'wedding'),  # flag: 2
    ('weddings', 'wedding'),  # flag: 2
    ('quinceanera', 'quinceanera'),  # flag: 2
    ('fencing', 'fencing'),  # flag: 2
    ('violin', 'violin2'),  # flag: 2
    ('violins', 'violin2'),  # flag: 2
    ('manicure', 'manicure'),  # flag: 2
    ('pedicure', 'manicure'),  # flag: 2
    ('manicures', 'manicure'),  # flag: 2
    ('pedicures', 'manicure'),  # flag: 2
    ('yoga', 'yoga'),  # flag: 2
    ('going for a walk', 'walk'),  # flag: 2
    ('walking', 'walk'),  # flag: 2
    ('french course', 'learnlanguage'),  # flag: 2
    ('german course', 'learnlanguage'),  # flag: 2
    ('english course', 'learnlanguage'),  # flag: 2
    ('italian course', 'learnlanguage'),  # flag: 2
    ('chinese course', 'learnlanguage'),  # flag: 2
    ('japanese course', 'learnlanguage'),  # flag: 2
    ('korean course', 'learnlanguage'),  # flag: 2
    ('polish course', 'learnlanguage'),  # flag: 2
    ('spanish course', 'learnlanguage'),  # flag: 2
    ('arabic course', 'learnlanguage'),  # flag: 2
    ('hebrew course', 'learnlanguage'),  # flag: 2
    ('portuguese course', 'learnlanguage'),  # flag: 2
    ('thai course', 'learnlanguage'),  # flag: 2
    ('russian course', 'learnlanguage'),  # flag: 2
    ('turkish course', 'learnlanguage'),  # flag: 2
    ('dutch course', 'learnlanguage'),  # flag: 2
    ('bulgarian course', 'learnlanguage'),  # flag: 2
    ('greek course', 'learnlanguage'),  # flag: 2
    ('hindi course', 'learnlanguage'),  # flag: 2
    ('indonesian course', 'learnlanguage'),  # flag: 2
    ('vietnamese course', 'learnlanguage'),  # flag: 2
    ('norwegian course', 'learnlanguage'),  # flag: 2
    ('swedish course', 'learnlanguage'),  # flag: 2
    ('slovenian course', 'learnlanguage'),  # flag: 2
    ('ukranian course', 'learnlanguage'),  # flag: 2
    ('slovak course', 'learnlanguage'),  # flag: 2
    ('lithuanian course', 'learnlanguage'),  # flag: 2
    ('latvian course', 'learnlanguage'),  # flag: 2
    ('hungarian course', 'learnlanguage'),  # flag: 2
    ('finnish course', 'learnlanguage'),  # flag: 2
    ('filipino course', 'learnlanguage'),  # flag: 2
    ('farsi course', 'learnlanguage'),  # flag: 2
    ('danish course', 'learnlanguage'),  # flag: 2
    ('czech course', 'learnlanguage'),  # flag: 2
    ('croatian course', 'learnlanguage'),  # flag: 2
    ('catalan course', 'learnlanguage'),  # flag: 2
    ('french class', 'learnlanguage'),  # flag: 2
    ('german class', 'learnlanguage'),  # flag: 2
    ('english class', 'learnlanguage'),  # flag: 2
    ('italian class', 'learnlanguage'),  # flag: 2
    ('chinese class', 'learnlanguage'),  # flag: 2
    ('japanese class', 'learnlanguage'),  # flag: 2
    ('korean class', 'learnlanguage'),  # flag: 2
    ('polish class', 'learnlanguage'),  # flag: 2
    ('spanish class', 'learnlanguage'),  # flag: 2
    ('arabic class', 'learnlanguage'),  # flag: 2
    ('hebrew class', 'learnlanguage'),  # flag: 2
    ('portuguese class', 'learnlanguage'),  # flag: 2
    ('thai class', 'learnlanguage'),  # flag: 2
    ('russian class', 'learnlanguage'),  # flag: 2
    ('turkish class', 'learnlanguage'),  # flag: 2
    ('dutch class', 'learnlanguage'),  # flag: 2
    ('bulgarian class', 'learnlanguage'),  # flag: 2
    ('greek class', 'learnlanguage'),  # flag: 2
    ('hindi class', 'learnlanguage'),  # flag: 2
    ('indonesian class', 'learnlanguage'),  # flag: 2
    ('vietnamese class', 'learnlanguage'),  # flag: 2
    ('norwegian class', 'learnlanguage'),  # flag: 2
    ('swedish class', 'learnlanguage'),  # flag: 2
    ('slovenian class', 'learnlanguage'),  # flag: 2
    ('ukranian class', 'learnlanguage'),  # flag: 2
    ('slovak class', 'learnlanguage'),  # flag: 2
    ('lithuanian class', 'learnlanguage'),  # flag: 2
    ('latvian class', 'learnlanguage'),  # flag: 2
    ('hungarian class', 'learnlanguage'),  # flag: 2
    ('finnish class', 'learnlanguage'),  # flag: 2
    ('filipino class', 'learnlanguage'),  # flag: 2
    ('farsi class', 'learnlanguage'),  # flag: 2
    ('danish class', 'learnlanguage'),  # flag: 2
    ('czech class', 'learnlanguage'),  # flag: 2
    ('croatian class', 'learnlanguage'),  # flag: 2
    ('catalan class', 'learnlanguage'),  # flag: 2
    ('practice french', 'learnlanguage'),  # flag: 2
    ('practice german', 'learnlanguage'),  # flag: 2
    ('practice english', 'learnlanguage'),  # flag: 2
    ('practice italian', 'learnlanguage'),  # flag: 2
    ('practice chinese', 'learnlanguage'),  # flag: 2
    ('practice japanese', 'learnlanguage'),  # flag: 2
    ('practice korean', 'learnlanguage'),  # flag: 2
    ('practice polish', 'learnlanguage'),  # flag: 2
    ('practice spanish', 'learnlanguage'),  # flag: 2
    ('practice arabic', 'learnlanguage'),  # flag: 2
    ('practice hebrew', 'learnlanguage'),  # flag: 2
    ('practice portuguese', 'learnlanguage'),  # flag: 2
    ('practice thai', 'learnlanguage'),  # flag: 2
    ('practice russian', 'learnlanguage'),  # flag: 2
    ('practice turkish', 'learnlanguage'),  # flag: 2
    ('practice dutch', 'learnlanguage'),  # flag: 2
    ('practice bulgarian', 'learnlanguage'),  # flag: 2
    ('practice greek', 'learnlanguage'),  # flag: 2
    ('practice hindi', 'learnlanguage'),  # flag: 2
    ('practice indonesian', 'learnlanguage'),  # flag: 2
    ('practice vietnamese', 'learnlanguage'),  # flag: 2
    ('practice norwegian', 'learnlanguage'),  # flag: 2
    ('practice swedish', 'learnlanguage'),  # flag: 2
    ('practice slovenian', 'learnlanguage'),  # flag: 2
    ('practice ukranian', 'learnlanguage'),  # flag: 2
    ('practice slovak', 'learnlanguage'),  # flag: 2
    ('practice lithuanian', 'learnlanguage'),  # flag: 2
    ('practice latvian', 'learnlanguage'),  # flag: 2
    ('practice hungarian', 'learnlanguage'),  # flag: 2
    ('practice finnish', 'learnlanguage'),  # flag: 2
    ('practice filipino', 'learnlanguage'),  # flag: 2
    ('practice farsi', 'learnlanguage'),  # flag: 2
    ('practice danish', 'learnlanguage'),  # flag: 2
    ('practice czech', 'learnlanguage'),  # flag: 2
    ('practice croatian', 'learnlanguage'),  # flag: 2
    ('practice catalan', 'learnlanguage'),  # flag: 2
    ('reach out to', 'reachout'),  # flag: 2
    ('write letter', 'reachout'),  # flag: 2
    ('send invitations', 'reachout'),  # flag: 2
    ('videogames', 'videogaming'),  # flag: 2
    ('videogaming', 'videogaming'),  # flag: 2
    ('video games', 'videogaming'),  # flag: 2
    ('video game', 'videogaming'),  # flag: 2
    ('video gaming', 'videogaming'),  # flag: 2
    ('walk the dog', 'walkingdog'),  # flag: 2
    ('dogsitting', 'walkingdog'),  # flag: 2
    ('dog sitting', 'walkingdog'),  # flag: 2
    ('walk dog', 'walkingdog'),  # flag: 2
    ('dog walking', 'walkingdog'),  # flag: 2
    ('dog walker', 'walkingdog'),  # flag: 2
    ('take dog out', 'walkingdog'),  # flag: 2
    ('take out dog', 'walkingdog'),  # flag: 2
    ('basketball', 'basketball'),  # flag: 2
    ('sleeping', 'sleep'),  # flag: 2
    ('resting', 'sleep'),  # flag: 2
    ('relaxing', 'sleep'),  # flag: 2
    ('napping', 'sleep'),  # flag: 2
    ('sleep', 'sleep'),  # flag: 2
    ('nap', 'sleep'),  # flag: 2
    ('climbing', 'climbing'),  # flag: 2
    ('bouldering', 'climbing'),  # flag: 2
    ('massage', 'massage'),  # flag: 2
    ('back rub', 'massage'),  # flag: 2
    ('backrub', 'massage'),  # flag: 2
    ('massages', 'massage'),  # flag: 2
    ('bbq', 'bbq'),  # flag: 2
    ('barbecue', 'bbq'),  # flag: 2
    ('barbeque', 'bbq'),  # flag: 2
    ('dinner', 'dinner'),  # flag: 2
    ('dinners', 'dinner'),  # flag: 2
    ('restaurant', 'dinner'),  # flag: 2
    ('restaurants', 'dinner'),  # flag: 2
    ('family meal', 'dinner'),  # flag: 2
    ('american football', 'americanfootball'),  # flag: 2
    ('superbowl', 'americanfootball'),  # flag: 2
    ('super bowl', 'americanfootball'),  # flag: 2
    ('football', 'americanfootball'),  # flag: 2
    ('archery', 'archery'),  # flag: 2
    ('opera', 'theatreopera'),  # flag: 2
    ('theatre', 'theatreopera'),  # flag: 2
    ('theater', 'theatreopera'),  # flag: 2
    ('soccer', 'soccer'),  # flag: 2
    ('tennis', 'tennis'),  # flag: 2
    ('sail', 'sailing'),  # flag: 2
    ('sailing', 'sailing'),  # flag: 2
    ('boat cruise', 'sailing'),  # flag: 2
    ('sailboat', 'sailing'),  # flag: 2
    ('gym', 'gym'),  # flag: 2
    ('workout', 'gym'),  # flag: 2
    ('workouts', 'gym'),  # flag: 2
    ('fitness program', 'gym'),  # flag: 2
    ('fitness class', 'gym'),  # flag: 2
    ('fitness test', 'gym'),  # flag: 2
    ('fitness evaluation', 'gym'),  # flag: 2
    ('fitness center', 'gym'),  # flag: 2
    ('fitness training', 'gym'),  # flag: 2
    ('weightlifting', 'gym'),  # flag: 2
    ('weight lifting', 'gym'),  # flag: 2
    ('crossfit', 'gym'),  # flag: 2
    ('skiing', 'skiing2'),  # flag: 2
    ('ski', 'skiing2'),  # flag: 2
    ('skis', 'skiing2'),  # flag: 2
    ('snowboarding', 'skiing2'),  # flag: 2
    ('snowshoeing', 'skiing2'),  # flag: 2
    ('snow shoe', 'skiing2'),  # flag: 2
    ('snow boarding', 'skiing2'),  # flag: 2
    ('volleyball', 'volleyball'),  # flag: 2
    ('hiking', 'hiking'),  # flag: 2
    ('hike', 'hiking'),  # flag: 2
    ('hikes', 'hiking'),  # flag: 2
    ('mardi gras', 'mardigras'),  # flag: 2
    ('mardigras', 'mardigras'),  # flag: 2
    ('shrove tuesday', 'mardigras'),  # flag: 2
    ('fat tuesday', 'mardigras'),  # flag: 2
    ('coffee', 'coffee'),  # flag: 2
    ('coffees', 'coffee'),  # flag: 2
    ('learn to code', 'code'),  # flag: 2
    ('coding time', 'code'),  # flag: 2
    ('hackathon', 'code'),  # flag: 2
    ('rails girls', 'code'),  # flag: 2
    ('railsgirls', 'code'),  # flag: 2
    ('hour of code', 'code'),  # flag: 2
    ('codecademy', 'code'),  # flag: 2
    ('computer science', 'code'),  # flag: 2
    ('programming in python', 'code'),  # flag: 2
    ('web programming', 'code'),  # flag: 2
    ('programming in java', 'code'),  # flag: 2
    ('web development', 'code'),  # flag: 2
    ('dentist', 'dentist'),  # flag: 2
    ('dentistry', 'dentist'),  # flag: 2
    ('dental', 'dentist'),  # flag: 2
    ('teeth cleaning', 'dentist'),  # flag: 3
    ('golf', 'golf'),  # flag: 2
    ('triathlon', 'triathlon'),  # flag: 2
    ('islamic new year', 'islamicnewyear'),  # flag: 4
    ('hijri new year', 'islamicnewyear'),  # flag: 4
    ('parsi new year', 'islamicnewyear'),  # flag: 4
    ('dyke march', 'pride'),  # flag: 2
    ('christopher street day', 'pride'),  # flag: 2
    ('gay parade', 'pride'),  # flag: 2
    ('gay pride', 'pride'),  # flag: 2
    ('gayglers', 'pride'),  # flag: 2
    ('gaygler', 'pride'),  # flag: 2
    ('lesbian march', 'pride'),  # flag: 2
    ('lesbian parade', 'pride'),  # flag: 2
    ('lesbian pride', 'pride'),  # flag: 2
    ('euro pride', 'pride'),  # flag: 2
    ('europride', 'pride'),  # flag: 2
    ('world pride', 'pride'),  # flag: 2
    ('worldpride', 'pride'),  # flag: 2
    ('gay & lesbian', 'pride'),  # flag: 2
    ('gay lesbian', 'pride'),  # flag: 2
    ('gay and lesbian', 'pride'),  # flag: 2
    ('breakfast', 'breakfast'),  # flag: 2
    ('breakfasts', 'breakfast'),  # flag: 2
    ('brunch', 'breakfast'),  # flag: 2
    ('brunches', 'breakfast'),  # flag: 2
    ('haircut', 'haircut'),  # flag: 2
    ('hairdresser', 'haircut'),  # flag: 2
    ('hair', 'haircut'),  # flag: 2
    ('lunch', 'lunch'),  # flag: 2
    ('lunches', 'lunch'),  # flag: 2
    ('luncheon', 'lunch'),  # flag: 2
    ('reading', 'read'),  # flag: 2
    ('newspaper', 'read'),  # flag: 2
    ('ebook', 'read'),  # flag: 2
    ('persian new year', 'nowruz'),  # flag: 4
    ('nowruz', 'nowruz'),  # flag: 4
    ('artistic gymnastics', 'artisticgymnastics'),  # flag: 2
    ('boardgames', 'gamenight'),  # flag: 2
    ('boardgame', 'gamenight'),  # flag: 2
    ('board games', 'gamenight'),  # flag: 2
    ('board game', 'gamenight'),  # flag: 2
    ('ping pong', 'pingpong'),  # flag: 2
    ('table tennis', 'pingpong'),  # flag: 4
    ('ping-pong', 'pingpong'),  # flag: 2
    ('pingpong', 'pingpong'),  # flag: 2
    ('handball', 'handball'),  # flag: 2
    ('wrestling', 'wrestling'),  # flag: 2
    ('chinese new year', 'chinesenewyear'),  # flag: 4
    ('chinese new years', 'chinesenewyear'),  # flag: 4
    ("chinese new year's", 'chinesenewyear'),  # flag: 4
    ('vietnamese new year', 'chinesenewyear'),  # flag: 4
    ('tết', 'chinesenewyear'),  # flag: 4
    ('chinese new year', 'chinesenewyear'),  # flag: 4
    ('chinese lunar new year', 'chinesenewyear'),  # flag: 4
    ('rowing', 'rowing'),  # flag: 2
    ('head of the charles', 'rowing'),  # flag: 2
    ('may bumps', 'rowing'),  # flag: 2
    ('head of the river race', 'rowing'),  # flag: 2
    ('shot put', 'athleticsthrowing'),  # flag: 2
    ('discus', 'athleticsthrowing'),  # flag: 2
    ('javelin', 'athleticsthrowing'),  # flag: 2
    ('hammer throw', 'athleticsthrowing'),  # flag: 2
    ('st patricks', 'saintpatricksday'),  # flag: 2
    ("st patrick's", 'saintpatricksday'),  # flag: 2
    ('bicycle', 'cycling'),  # flag: 2
    ('cycling', 'cycling'),  # flag: 2
    ('bike', 'cycling'),  # flag: 2
    ('bicycles', 'cycling'),  # flag: 2
    ('bikes', 'cycling'),  # flag: 2
    ('biking', 'cycling'),  # flag: 2
    ('mountain biking', 'cycling'),  # flag: 2
    ('mountain bike', 'cycling'),  # flag: 2
    ('karate', 'karate'),  # flag: 2
    ('judo', 'karate'),  # flag: 2
    ('taekwondo', 'karate'),  # flag: 2
    ('martial arts', 'karate'),  # flag: 2
    ('jujutsu', 'karate'),  # flag: 2
    ('aikido', 'karate'),  # flag: 2
    ('jiu-jitsu', 'karate'),  # flag: 2
    ('jiu jitsu', 'karate'),  # flag: 2
    ('halloween', 'halloween'),  # flag: 2
    ('helloween', 'halloween'),  # flag: 2
    ("hallowe'en", 'halloween'),  # flag: 2
    ('allhalloween', 'halloween'),  # flag: 2
    ("all hallows' eve", 'halloween'),  # flag: 2
    ("all saints' eve", 'halloween'),  # flag: 2
    ('concert', 'concert'),  # flag: 2
    ('gig', 'concert'),  # flag: 2
    ('concerts', 'concert'),  # flag: 2
    ('gigs', 'concert'),  # flag: 2
    ('movie', 'cinema'),  # flag: 2
    ('cinema', 'cinema'),  # flag: 2
    ('movies', 'cinema'),  # flag: 2
    ('baseball', 'baseball'),  # flag: 2
    ('piano', 'learninstrument'),  # flag: 2
    ('singing', 'learninstrument'),  # flag: 2
    ('music class', 'learninstrument'),  # flag: 2
    ('choir practice', 'learninstrument'),  # flag: 2
    ('flute', 'learninstrument'),  # flag: 2
    ('orchestra', 'learninstrument'),  # flag: 2
    ('oboe', 'learninstrument'),  # flag: 2
    ('clarinet', 'learninstrument'),  # flag: 2
    ('saxophone', 'learninstrument'),  # flag: 2
    ('cornett', 'learninstrument'),  # flag: 2
    ('trumpet', 'learninstrument'),  # flag: 2
    ('contrabass', 'learninstrument'),  # flag: 2
    ('cello', 'learninstrument'),  # flag: 2
    ('trombone', 'learninstrument'),  # flag: 2
    ('tuba', 'learninstrument'),  # flag: 2
    ('music ensemble', 'learninstrument'),  # flag: 2
    ('string quartett', 'learninstrument'),  # flag: 2
    ('guitar lesson', 'learninstrument'),  # flag: 2
    ('classical music', 'learninstrument'),  # flag: 2
    ('choir', 'learninstrument'),  # flag: 2
    ('rhythmic gymnastics', 'rhythmicgymnastics'),  # flag: 2
    ('jumping', 'athleticsjumping'),  # flag: 2
    ('bowling', 'bowling'),  # flag: 2
    ('valentines day', 'valentinesday'),  # flag: 2
    ('valentine day', 'valentinesday'),  # flag: 2
    ("valentine's day", 'valentinesday'),  # flag: 2
    ('beer', 'beer'),  # flag: 2
    ('beers', 'beer'),  # flag: 2
    ('oktoberfest', 'beer'),  # flag: 2
    ('october fest', 'beer'),  # flag: 2
    ('octoberfest', 'beer'),  # flag: 2
    ('christmas party', 'xmasparty'),  # flag: 4
    ('xmas party', 'xmasparty'),  # flag: 4
    ('x-mas party', 'xmasparty'),  # flag: 4
    ('christmas eve party', 'xmasparty'),  # flag: 4
    ('xmas eve party', 'xmasparty'),  # flag: 4
    ('x-mas eve party', 'xmasparty'),  # flag: 4
    ('badminton', 'badminton'),  # flag: 2
    ('plan week', 'planmyday'),  # flag: 2
    ('plan quarter', 'planmyday'),  # flag: 2
    ('plan day', 'planmyday'),  # flag: 2
    ('plan vacation', 'planmyday'),  # flag: 2
    ('week planning', 'planmyday'),  # flag: 2
    ('vacation planning', 'planmyday'),  # flag: 2
    ('bmx', 'cyclingbmx'),  # flag: 2
    ('camping', 'camping'),  # flag: 2
    ('painting', 'art'),  # flag: 2
    ('art workshop', 'art'),  # flag: 2
    ('art workshops', 'art'),  # flag: 2
    ('sketching workshop', 'art'),  # flag: 2
    ('drawing workshop', 'art'),  # flag: 2
    ('dance', 'dancing'),  # flag: 2
    ('dancing', 'dancing'),  # flag: 2
    ('dances', 'dancing'),  # flag: 2
    ('ballet', 'dancing'),  # flag: 2
    ('water polo', 'waterpolo'),  # flag: 2
    ('waterpolo', 'waterpolo'),  # flag: 2
    ('christmas dinner', 'xmasmeal'),  # flag: 5
    ('christmas lunch', 'xmasmeal'),  # flag: 5
    ('christmas brunch', 'xmasmeal'),  # flag: 5
    ('christmas luncheon', 'xmasmeal'),  # flag: 5
    ('xmas dinner', 'xmasmeal'),  # flag: 5
    ('xmas lunch', 'xmasmeal'),  # flag: 5
    ('xmas brunch', 'xmasmeal'),  # flag: 5
    ('xmas luncheon', 'xmasmeal'),  # flag: 5
    ('x-mas dinner', 'xmasmeal'),  # flag: 5
    ('x-mas lunch', 'xmasmeal'),  # flag: 5
    ('x-mas brunch', 'xmasmeal'),  # flag: 5
    ('x-mas luncheon', 'xmasmeal'),  # flag: 5
    ('christmas eve dinner', 'xmasmeal'),  # flag: 5
    ('christmas eve lunch', 'xmasmeal'),  # flag: 5
    ('christmas eve brunch', 'xmasmeal'),  # flag: 5
    ('christmas eve luncheon', 'xmasmeal'),  # flag: 5
    ('xmas eve dinner', 'xmasmeal'),  # flag: 5
    ('xmas eve lunch', 'xmasmeal'),  # flag: 5
    ('xmas eve brunch', 'xmasmeal'),  # flag: 5
    ('xmas eve luncheon', 'xmasmeal'),  # flag: 5
    ('x-mas eve dinner', 'xmasmeal'),  # flag: 5
    ('x-mas eve lunch', 'xmasmeal'),  # flag: 5
    ('x-mas eve brunch', 'xmasmeal'),  # flag: 5
    ('x-mas eve luncheon', 'xmasmeal'),  # flag: 5
    ('clean the house', 'clean'),  # flag: 2
    ('clean the apartment', 'clean'),  # flag: 2
    ('clean house', 'clean'),  # flag: 2
    ('tidy up', 'clean'),  # flag: 2
    ('vacuum clean', 'clean'),  # flag: 2
    ('vacuum cleaning', 'clean'),  # flag: 2
    ('shooting sport', 'shooting'),  # flag: 2
    ('shooting sports', 'shooting'),  # flag: 2
    ('shooting competition', 'shooting'),  # flag: 2
    ('competitive shooting', 'shooting'),  # flag: 2
    ('graduation', 'graduation'),  # flag: 2
    ('oil change', 'oilchange'),  # flag: 2
    ('car service', 'oilchange'),  # flag: 2
    ('rugby', 'rugbysevens'),  # flag: 2
    ('swim', 'swimming'),  # flag: 2
    ('swimming', 'swimming'),  # flag: 2
    ('swims', 'swimming'),  # flag: 2
    ('diving', 'swimming'),  # flag: 2
    ('synchronized swimming', 'swimming'),  # flag: 2
    ('boxing', 'boxing'),  # flag: 2
    ('cricket game', 'cricket'),  # flag: 2
    ('cricket match', 'cricket'),  # flag: 2
    ('cricket competition', 'cricket'),  # flag: 2
    ('car repair', 'carmaintenance'),  # flag: 2
    ('auto repair', 'carmaintenance'),  # flag: 2
    ('car maintenance', 'carmaintenance'),  # flag: 2
    ('auto maintenance', 'carmaintenance'),  # flag: 2
    ('car mechanic', 'carmaintenance'),  # flag: 2
    ('auto mechanic', 'carmaintenance'),  # flag: 2
    ('tire replacement', 'carmaintenance'),  # flag: 2
    ('tire change', 'carmaintenance'),  # flag: 2
    ('field hockey', 'fieldhockey'),  # flag: 2
    ('billiard', 'billiard'),  # flag: 2
)


def match(name):
    """Given an event name like "Board Game Night!", return a URL to a relevant icon."""

    name = ' %s ' % name.lower()
    for table, base in ((GOOGLE_TABLE, GOOGLE_PATTERN),):
        for phrase, identifier in table:
            if re.search(re.escape(' %s ' % phrase).replace(r'\ ', r'\W+'), name):
                return base % identifier


if __name__ == '__main__':
    import os
    import sys

    from metabot.util import protobuf

    class _FlairPhrase(protobuf.ProtoBuf):  # pylint: disable=too-few-public-methods
        _fields = (
            (1, 'flag', int),
            (2, 'phrase', str),
        )

    class _FlairEntry(protobuf.ProtoBuf):  # pylint: disable=too-few-public-methods
        _fields = (
            (1, 'identifier', str),
            (2, 'phrases', _FlairPhrase, list),
        )

    class _FlairFile(protobuf.ProtoBuf):  # pylint: disable=too-few-public-methods
        _fields = (
            (1, 'entries', _FlairEntry, list),
            (2, 'lang_code', str),
        )

    def main(argv):  # pylint: disable=missing-docstring,too-many-branches,too-many-locals
        if len(argv) < 2:
            print('USAGE: %s path/to/assets/flairs/flairdata_en.pb' % sys.argv[0])
            return 1

        flair = _FlairFile(list(open(argv[1], 'rb').read()))

        lines = open(__file__, 'r').read().splitlines()
        with open(__file__ + '.new', 'w') as fobj:
            i = 0
            for i, line in enumerate(lines):
                fobj.write(line + '\n')
                if line == 'GOOGLE_TABLE = (':
                    break
            fobj.write('    # Language code: %s\n' % flair.lang_code)  # pylint: disable=no-member
            for identifier, phrases in flair.entries:  # pylint: disable=no-member
                for flag, phrase in phrases:
                    fobj.write('    %r,  # flag: %r\n' % ((phrase.lower(), identifier), flag))
            while lines[i] != ')':
                i += 1
            while i < len(lines):
                fobj.write(lines[i] + '\n')
                i += 1
        os.rename(__file__ + '.new', __file__)

    sys.exit(main(sys.argv))
