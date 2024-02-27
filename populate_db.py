import random
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from ticketsystem.models import Club, Event, Friend, Follow, Ticket
from ticketsystem.utils import ticketQRCodeGenerator, ticketCodeGenerator
from django.core.files.base import ContentFile

User = get_user_model()

# User and Profile
users_data = {
    'Ava Johnson': {
        'student_id': 102345,
        "bio": "Hey there! I'm Ava Johnson, a spirited university student with a heart full of creativity and a love for vibrant events. University life, to me, is a kaleidoscope of opportunities where I get to explore my artistic side. As an active member of the Art Club, I find immense joy in turning blank canvases into expressive stories. University events are my playground to meet new people, share ideas, and create memories that last a lifetime. In the future, I dream of merging my artistic passion with technology, perhaps bringing a touch of innovation to visual storytelling."
    },
    'Olivia Smith': {
        'student_id': 209876,
        "bio": "Hello, world! I'm Olivia Smith, a perpetual learner navigating the exciting journey of university life. The diverse events on campus are my source of inspiration, sparking my curiosity and fueling my thirst for knowledge. As a firm believer in the power of education, I actively engage in various activities that expand my horizons. In the future, I aspire to contribute to educational advancements, making learning more accessible and enjoyable. University events, with their dynamic atmosphere, provide the perfect backdrop for connecting with like-minded individuals and building friendships that go beyond the classroom."
    },
    'Sophia Brown': {
        'student_id': 315678,
        "bio": "Greetings! I'm Sophia Brown, a university enthusiast with a penchant for community and connection. University events are my go-to place for meeting new people, sharing laughter, and creating bonds that make this journey unforgettable. As a sociable soul, I thrive on the energy of campus gatherings. In the future, I envision myself working in a field where I can make a positive impact on communities, fostering inclusivity and understanding. Join me at the next university event, and let's make memories that echo through our college years!"
    },
    'Emma Davis': {
        'student_id': 420987,
        "bio": "Hi, everyone! I'm Emma Davis, a university adventurer on a quest for knowledge and memorable experiences. University events, to me, are like stepping stones in this journey of self-discovery. Engaging in diverse activities, I find joy in expanding my horizons and embracing the rich tapestry of campus life. My future aspirations revolve around combining my passion for environmental sustainability with community outreach. University events offer the perfect stage for connecting with eco-conscious minds and working together to create a positive impact on our world."
    },
    'Mia Anderson': {
        'student_id': 537890,
        "bio": "Hey, lovely souls! I'm Mia Anderson, a university dreamer with a heart full of aspirations and a love for meaningful connections. University events are my playground for exploration, where I dive into various activities to uncover new passions and meet inspiring individuals. In the future, I see myself making a difference in the world of social justice, advocating for causes that bring positive change. Join me at the next event, and let's create a vibrant tapestry of memories that define our university years!"
    },
    'Isabella Taylor': {
        'student_id': 641234,
        "bio": "Salutations! I'm Isabella Taylor, a spirited university explorer fueled by curiosity and a love for diverse experiences. University events, with their kaleidoscope of activities, are my playground for meeting new people and embracing the rich tapestry of campus life. As an active member of the Chess Club, I find joy in strategic thinking and building connections through shared interests. In the future, I envision a career where I can blend my analytical skills with creativity, leaving a lasting impact on the world. Join me at the next event, and let's create memories that color our university journey!"
    },
    'Harper Martinez': {
        'student_id': 758901,
        "bio": "Hola amigos! I'm Harper Martinez, a university soul with a zest for life and a love for connecting with diverse minds. University events are my sanctuary for cultural exploration and building bridges of understanding. Engaging in the Dance Club, I celebrate the joy of movement and the unity it brings. In the future, I aspire to bridge cultural gaps through the universal language of dance. Join me at the next event, and let's sway to the rhythm of friendship and shared experiences!"
    },
    'Evelyn Hernandez': {
        'student_id': 864321,
        "bio": "Hola, queridos! I'm Evelyn Hernandez, a passionate university student with a heart set on exploration and cultural celebration. University events are my canvas for discovering new perspectives and building connections that transcend borders. As a proud member of the Photography Club, I capture moments that tell stories and celebrate the beauty of diversity. In the future, I dream of merging my love for photography with humanitarian efforts, using visuals to create awareness and inspire change. Join me at the next event, and let's capture memories that resonate through our university journey!"
    },
    'Amelia Robinson': {
        'student_id': 970123,
        "bio": "Greetings, kindred spirits! I'm Amelia Robinson, a university dreamer weaving my story through the vibrant fabric of campus life. University events are my palette for self-expression and connecting with fellow dreamers. Embracing the world of music in the Music Club, I find solace and joy in the harmonies that unite us. In the future, I envision a career where I can infuse creativity into everyday life, leaving traces of inspiration wherever I go. Join me at the next event, and let's create melodies of friendship and shared experiences!"
    },
    'Abigail White': {
        'student_id': 108765,
        "bio": "Hello, world! I'm Abigail White, a spirited university soul with a heart for adventure and a love for making lasting connections. University events, with their dynamic energy, are my playground for exploration and meeting like-minded individuals. As a member of the Badminton Club, I thrive on the adrenaline of competition and the camaraderie it brings. In the future, I see myself embracing challenges, both on and off the court, and making a positive impact on the world. Join me at the next event, and let's make memories that echo through our university journey!"
    },
    'Liam Miller': {
        'student_id': 117890,
        "bio": "Hey, everyone! I'm Liam Miller, a university adventurer with a passion for learning and a love for making the most of every moment. University events, to me, are like chapters in a thrilling book, each offering new lessons and experiences. Engaging in the world of coding in the Coding Club, I find joy in unraveling the mysteries of technology and collaborating with fellow innovators. In the future, I envision myself shaping the digital landscape with creativity and problem-solving. Join me at the next event, and let's code a future filled with exciting possibilities!"
    },
    'Noah Wilson': {
        'student_id': 126543,
        "bio": "Greetings, fellow explorers! I'm Noah Wilson, a university enthusiast with a penchant for discovery and a love for creating connections. University events, with their diverse array of activities, are my playground for meeting inspiring individuals and building bonds that last a lifetime. As an active member of the Investing Society, I navigate the world of finance with a curiosity for smart investing and financial literacy. In the future, I see myself making informed decisions that impact the world positively. Join me at the next event, and let's invest in creating memories and friendships!"
    },
    'Jackson Davis': {
        'student_id': 135678,
        "bio": "Hello, universe! I'm Jackson Davis, a university dreamer with a heart set on exploration and a love for diverse experiences. University events, with their dynamic energy, are my canvas for self-expression and connecting with fellow dreamers. Engaging in the world of debate in the Debate Club, I find joy in articulating ideas and engaging in thought-provoking discussions. In the future, I see myself advocating for positive change through the power of words. Join me at the next event, and let's debate, discuss, and create memories that shape our university journey!"
    },
    'Aiden Thompson': {
        'student_id': 144321,
        "bio": "Hey, world! I'm Aiden Thompson, a university soul with a passion for adventure and a love for making every moment count. University events, with their vibrant atmosphere, are my playground for exploration and meeting like-minded individuals. As a member of the Basketball Club, I thrive on the adrenaline of the game and the camaraderie it brings. In the future, I envision myself embracing challenges, both on and off the court, and making a positive impact on the world. Join me at the next event, and let's make memories that echo through our university journey!"
    },
    'Lucas Garcia': {
        'student_id': 153456,
        "bio": "Hola, amigos! I'm Lucas Garcia, a spirited university soul with a zest for life and a love for connecting with diverse minds. University events are my sanctuary for cultural exploration and building bridges of understanding. Engaging in the Dance Club, I celebrate the joy of movement and the unity it brings. In the future, I aspire to bridge cultural gaps through the universal language of dance. Join me at the next event, and let's sway to the rhythm of friendship and shared experiences!"
    },
    'Elijah Turner': {
        'student_id': 162987,
        "bio": "Greetings, kindred spirits! I'm Elijah Turner, a university dreamer weaving my story through the vibrant fabric of campus life. University events are my palette for self-expression and connecting with fellow dreamers. Embracing the world of music in the Music Club, I find solace and joy in the harmonies that unite us. In the future, I envision a career where I can infuse creativity into everyday life, leaving traces of inspiration wherever I go. Join me at the next event, and let's create melodies of friendship and shared experiences!"
    },
    'Oliver Parker': {
        'student_id': 171234,
        "bio": "Hello, world! I'm Oliver Parker, a spirited university soul with a heart for adventure and a love for making lasting connections. University events, with their dynamic energy, are my playground for exploration and meeting like-minded individuals. As a member of the Badminton Club, I thrive on the adrenaline of competition and the camaraderie it brings. In the future, I see myself embracing challenges, both on and off the court, and making a positive impact on the world. Join me at the next event, and let's make memories that echo through our university journey!"
    },
    'Mason Scott': {
        'student_id': 189076,
        "bio": "Hey, everyone! I'm Mason Scott, a university adventurer with a passion for learning and a love for making the most of every moment. University events, to me, are like chapters in a thrilling book, each offering new lessons and experiences. Engaging in the world of coding in the Coding Club, I find joy in unraveling the mysteries of technology and collaborating with fellow innovators. In the future, I envision myself shaping the digital landscape with creativity and problem-solving. Join me at the next event, and let's code a future filled with exciting possibilities!"
    },
    'Ethan Harris': {
        'student_id': 20240011,
        "bio": "Greetings, fellow explorers! I'm Ethan Harris, a university enthusiast with a penchant for discovery and a love for creating connections. University events, with their diverse array of activities, are my playground for meeting inspiring individuals and building bonds that last a lifetime. As an active member of the Investing Society, I navigate the world of finance with a curiosity for smart investing and financial literacy. In the future, I see myself making informed decisions that impact the world positively. Join me at the next event, and let's invest in creating memories and friendships!"
    },
    'Alexander Mitchell': {
        'student_id': 20240022,
        "bio": "Hello, universe! I'm Alexander Mitchell, a university dreamer with a heart set on exploration and a love for diverse experiences. University events, with their dynamic energy, are my canvas for self-expression and connecting with fellow dreamers. Engaging in the world of debate in the Debate Club, I find joy in articulating ideas and engaging in thought-provoking discussions. In the future, I see myself advocating for positive change through the power of words. Join me at the next event, and let's debate, discuss, and create memories that shape our university journey!"
    },
    'Juliette Thompson': {
        'student_id': 20240033,
        "bio": "Hey, world! I'm Juliette Thompson, a university soul with a passion for adventure and a love for making every moment count. University events, with their vibrant atmosphere, are my playground for exploration and meeting like-minded individuals. As a member of the Basketball Club, I thrive on the adrenaline of the game and the camaraderie it brings. In the future, I envision myself embracing challenges, both on and off the court, and making a positive impact on the world. Join me at the next event, and let's make memories that echo through our university journey!"
    },
    'Esther Rodriguez': {
        'student_id': 20240044,
        "bio": "Hola, amigos! I'm Esther Rodriguez, a spirited university soul with a zest for life and a love for connecting with diverse minds. University events are my sanctuary for cultural exploration and building bridges of understanding. Engaging in the Dance Club, I celebrate the joy of movement and the unity it brings. In the future, I aspire to bridge cultural gaps through the universal language of dance. Join me at the next event, and let's sway to the rhythm of friendship and shared experiences!"
    },
    'Maria Patel': {
        'student_id': 20240055,
        "bio": "Hola, queridos! I'm Maria Patel, a passionate university student with a heart set on exploration and cultural celebration. University events are my canvas for discovering new perspectives and building connections that transcend borders. As a proud member of the Photography Club, I capture moments that tell stories and celebrate the beauty of diversity. In the future, I dream of merging my love for photography with humanitarian efforts, using visuals to create awareness and inspire change. Join me at the next event, and let's capture memories that resonate through our university journey!"
    },
    'Marta Campbell': {
        'student_id': 20240066,
        "bio": "Greetings, kindred spirits! I'm Marta Campbell, a university dreamer weaving my story through the vibrant fabric of campus life. University events are my palette for self-expression and connecting with fellow dreamers. Embracing the world of music in the Music Club, I find solace and joy in the harmonies that unite us. In the future, I envision a career where I can infuse creativity into everyday life, leaving traces of inspiration wherever I go. Join me at the next event, and let's create melodies of friendship and shared experiences!"
    },
    'Lily Nguyen': {
        'student_id': 20240077,
        "bio": "Hello, world! I'm Lily Nguyen, a spirited university soul with a heart for adventure and a love for making lasting connections. University events, with their dynamic energy, are my playground for exploration and meeting like-minded individuals. As a member of the Badminton Club, I thrive on the adrenaline of competition and the camaraderie it brings. In the future, I see myself embracing challenges, both on and off the court, and making a positive impact on the world. Join me at the next event, and let's make memories that echo through our university journey!"
    },
    'John Wilson': {
        'student_id': 20240088,
        "bio": "Hey, everyone! I'm John Wilson, a university adventurer with a passion for learning and a love for making the most of every moment. University events, to me, are like chapters in a thrilling book, each offering new lessons and experiences. Engaging in the world of coding in the Coding Club, I find joy in unraveling the mysteries of technology and collaborating with fellow innovators. In the future, I envision myself shaping the digital landscape with creativity and problem-solving. Join me at the next event, and let's code a future filled with exciting possibilities!"
    },
    'Manuel Lee': {
        'student_id': 20240099,
        "bio": "Hola, amigos! I'm Manuel Lee, a spirited university soul with a zest for life and a love for connecting with diverse minds. University events are my sanctuary for cultural exploration and building bridges of understanding. Engaging in the Dance Club, I celebrate the joy of movement and the unity it brings. In the future, I aspire to bridge cultural gaps through the universal language of dance. Join me at the next event, and let's sway to the rhythm of friendship and shared experiences!"
    },
    'Rodrigo Kim': {
        'student_id': 20240100,
        "bio": "Greetings, kindred spirits! I'm Rodrigo Kim, a university dreamer weaving my story through the vibrant fabric of campus life. University events are my palette for self-expression and connecting with fellow dreamers. Embracing the world of music in the Music Club, I find solace and joy in the harmonies that unite us. In the future, I envision a career where I can infuse creativity into everyday life, leaving traces of inspiration wherever I go. Join me at the next event, and let's create melodies of friendship and shared experiences!"
    },
    'Luis Murphy': {
        'student_id': 20240101,
        "bio": "Hello, world! I'm Luis Murphy, a spirited university soul with a heart for adventure and a love for making lasting connections. University events, with their dynamic energy, are my playground for exploration and meeting like-minded individuals. As a member of the Badminton Club, I thrive on the adrenaline of competition and the camaraderie it brings. In the future, I see myself embracing challenges, both on and off the court, and making a positive impact on the world. Join me at the next event, and let's make memories that echo through our university journey!"
    },
    'Aaron Wright': {
        'student_id': 20240102,
        "bio": "Hey, everyone! I'm Aaron Wright, a university adventurer with a passion for learning and a love for making the most of every moment. University events, to me, are like chapters in a thrilling book, each offering new lessons and experiences. Engaging in the world of coding in the Coding Club, I find joy in unraveling the mysteries of technology and collaborating with fellow innovators. In the future, I envision myself shaping the digital landscape with creativity and problem-solving. Join me at the next event, and let's code a future filled with exciting possibilities!"
    },
    'Sabrina White': {
        'student_id': 20240112,
        "bio": "Hey, everyone! I'm Sabrina White, a university adventurer with a passion for exploring the world of literature and a love for creating connections. University events, to me, are like pages of a captivating novel, each filled with new stories and opportunities. As an active member of the Book Club, I find joy in sharing my favorite stories and discovering new literary gems. In the future, I see myself contributing to the world of storytelling, either through writing or editorial work. Join me at the next book discussion, and let's embark on a literary journey together!"
    },
    'Alvaro Davis': {
        'student_id': 20240113,
        "bio": "Greetings, fellow learners! I'm Alvaro Davis, a university enthusiast with a passion for unraveling the mysteries of the natural world and a love for making meaningful connections. University events, with their diverse range of activities, are my playground for exploration and meeting like-minded individuals. As a member of the Environmental Science Club, I find joy in understanding and advocating for the planet. In the future, I envision myself contributing to environmental conservation and sustainable practices. Join me at the next eco-friendly event, and let's make a positive impact together!"
    },
    'Aria Martinez': {
        'student_id': 20240114,
        "bio": "Hola, amigos! I'm Aria Martinez, a spirited university soul with a zest for life and a love for connecting with diverse minds. University events are my sanctuary for cultural exploration and building bridges of understanding. Engaging in the Dance Club, I celebrate the joy of movement and the unity it brings. In the future, I aspire to bridge cultural gaps through the universal language of dance. Join me at the next event, and let's sway to the rhythm of friendship and shared experiences!"
    },
    'Elias Brown': {
        'student_id': 20240115,
        "bio": "Hello, universe! I'm Elias Brown, a university dreamer with a heart set on exploration and a love for diverse experiences. University events, with their dynamic energy, are my canvas for self-expression and connecting with fellow dreamers. Engaging in the world of debate in the Debate Club, I find joy in articulating ideas and engaging in thought-provoking discussions. In the future, I see myself advocating for positive change through the power of words. Join me at the next event, and let's debate, discuss, and create memories that shape our university journey!"
    },
    'Grace Taylor': {
        'student_id': 20240116,
        "bio": "Hey, lovely souls! I'm Grace Taylor, a university dreamer with a heart full of aspirations and a love for meaningful connections. University events are my playground for exploration, where I dive into various activities to uncover new passions and meet inspiring individuals. In the future, I see myself making a difference in the world of social justice, advocating for causes that bring positive change. Join me at the next event, and let's create a vibrant tapestry of memories that define our university years!"
    },
    'Henry Wilson': {
        'student_id': 20240117,
        "bio": "Greetings, fellow explorers! I'm Henry Wilson, a university enthusiast with a penchant for discovery and a love for creating connections. University events, with their diverse array of activities, are my playground for meeting inspiring individuals and building bonds that last a lifetime. As an active member of the Investing Society, I navigate the world of finance with a curiosity for smart investing and financial literacy. In the future, I see myself making informed decisions that impact the world positively. Join me at the next event, and let's invest in creating memories and friendships!"
    },
    'Sophie Rodriguez': {
        'student_id': 20240118,
        "bio": "Hola, queridos! I'm Sophie Rodriguez, a passionate university student with a heart set on exploration and cultural celebration. University events are my canvas for discovering new perspectives and building connections that transcend borders. As a proud member of the Photography Club, I capture moments that tell stories and celebrate the beauty of diversity. In the future, I dream of merging my love for photography with humanitarian efforts, using visuals to create awareness and inspire change. Join me at the next event, and let's capture memories that resonate through our university journey!"
    },
    'Leo Nguyen': {
        'student_id': 20240119,
        "bio": "Hello, world! I'm Leo Nguyen, a spirited university soul with a heart for adventure and a love for making lasting connections. University events, with their dynamic energy, are my playground for exploration and meeting like-minded individuals. As a member of the Badminton Club, I thrive on the adrenaline of competition and the camaraderie it brings. In the future, I see myself embracing challenges, both on and off the court, and making a positive impact on the world. Join me at the next event, and let's make memories that echo through our university journey!"
    },
    'Adonis Smith': {
        'student_id': 20240120,
        "bio": "Hey, everyone! I'm Adonis Smith, a university adventurer with a passion for learning and a love for making the most of every moment. University events, to me, are like chapters in a thrilling book, each offering new lessons and experiences. Engaging in the world of coding in the Coding Club, I find joy in unraveling the mysteries of technology and collaborating with fellow innovators. In the future, I envision myself shaping the digital landscape with creativity and problem-solving. Join me at the next event, and let's code a future filled with exciting possibilities!"
    },
    'Lila Harris': {
        'student_id': 20240121,
        "bio": "Greetings, kindred spirits! I'm Lila Harris, a university dreamer weaving my story through the vibrant fabric of campus life. University events are my palette for self-expression and connecting with fellow dreamers. Embracing the world of music in the Music Club, I find solace and joy in the harmonies that unite us. In the future, I envision a career where I can infuse creativity into everyday life, leaving traces of inspiration wherever I go. Join me at the next event, and let's create melodies of friendship and shared experiences!"
    },
    'Milo Scott': {
        'student_id': 20240122,
        "bio": "Hey, everyone! I'm Milo Scott, a university adventurer with a passion for learning and a love for making the most of every moment. University events, to me, are like chapters in a thrilling book, each offering new lessons and experiences. Engaging in the world of coding in the Coding Club, I find joy in unraveling the mysteries of technology and collaborating with fellow innovators. In the future, I envision myself shaping the digital landscape with creativity and problem-solving. Join me at the next event, and let's code a future filled with exciting possibilities!"
    },
    'Martina Turner': {
        'student_id': 20240123,
        "bio": "Greetings, fellow learners! I'm Martina Turner, a university enthusiast with a passion for unraveling the mysteries of the natural world and a love for making meaningful connections. University events, with their diverse range of activities, are my playground for exploration and meeting like-minded individuals. As a member of the Environmental Science Club, I find joy in understanding and advocating for the planet. In the future, I envision myself contributing to environmental conservation and sustainable practices. Join me at the next eco-friendly event, and let's make a positive impact together!"
    },
    'Benji White': {
        'student_id': 20240124,
        "bio": "Hello, universe! I'm Benji White, a university dreamer with a heart set on exploration and a love for diverse experiences. University events, with their dynamic energy, are my canvas for self-expression and connecting with fellow dreamers. Engaging in the world of debate in the Debate Club, I find joy in articulating ideas and engaging in thought-provoking discussions. In the future, I see myself advocating for positive change through the power of words. Join me at the next event, and let's debate, discuss, and create memories that shape our university journey!"
    },
    'Patricia Davis': {
        'student_id': 20240125,
        "bio": "Hey, lovely souls! I'm Patricia Davis, a university dreamer with a heart full of aspirations and a love for meaningful connections. University events are my playground for exploration, where I dive into various activities to uncover new passions and meet inspiring individuals. In the future, I see myself making a difference in the world of social justice, advocating for causes that bring positive change. Join me at the next event, and let's create a vibrant tapestry of memories that define our university years!"
    },
    'Alejandro Taylor': {
        'student_id': 20240126,
        "bio": "Greetings, fellow explorers! I'm Lucas Alejandro, a university enthusiast with a penchant for discovery and a love for creating connections. University events, with their diverse array of activities, are my playground for meeting inspiring individuals and building bonds that last a lifetime. As an active member of the Investing Society, I navigate the world of finance with a curiosity for smart investing and financial literacy. In the future, I see myself making informed decisions that impact the world positively. Join me at the next event, and let's invest in creating memories and friendships!"
    },
    'Inma Rodriguez': {
        'student_id': 20240127,
        "bio": "Hola, queridos! I'm Inma Rodriguez, a passionate university student with a heart set on exploration and cultural celebration. University events are my canvas for discovering new perspectives and building connections that transcend borders. As a proud member of the Photography Club, I capture moments that tell stories and celebrate the beauty of diversity. In the future, I dream of merging my love for photography with humanitarian efforts, using visuals to create awareness and inspire change. Join me at the next event, and let's capture memories that resonate through our university journey!"
    },
    'Pablo Murphy': {
        'student_id': 20240128,
        "bio": "Greetings, kindred spirits! I'm Pablo Murphy, a university dreamer weaving my story through the vibrant fabric of campus life. University events are my palette for self-expression and connecting with fellow dreamers. Embracing the world of music in the Music Club, I find solace and joy in the harmonies that unite us. In the future, I envision a career where I can infuse creativity into everyday life, leaving traces of inspiration wherever I go. Join me at the next event, and let's create melodies of friendship and shared experiences!"
    },
    'Millilie Turner': {
        'student_id': 20240129,
        "bio": "Hey, everyone! I'm Millilie Turner, a university adventurer with a passion for learning and a love for making the most of every moment. University events, to me, are like chapters in a thrilling book, each offering new lessons and experiences. Engaging in the world of coding in the Coding Club, I find joy in unraveling the mysteries of technology and collaborating with fellow innovators. In the future, I envision myself shaping the digital landscape with creativity and problem-solving. Join me at the next event, and let's code a future filled with exciting possibilities!"
    },
    'Jervin Baylon': {
        'student_id': 20240130,
        "bio": "Greetings, fellow learners! I'm Jervin Baylon, a university enthusiast with a passion for unraveling the mysteries of the natural world and a love for making meaningful connections. University events, with their diverse range of activities, are my playground for exploration and meeting like-minded individuals. As a member of the Environmental Science Club, I find joy in understanding and advocating for the planet. In the future, I envision myself contributing to environmental conservation and sustainable practices. Join me at the next eco-friendly event, and let's make a positive impact together!"
    },
    'Rita Brown': {
        'student_id': 20240131,
        "bio": "Hola, amigos! I'm Rita Brown, a spirited university soul with a zest for life and a love for connecting with diverse minds. University events are my sanctuary for cultural exploration and building bridges of understanding. Engaging in the Dance Club, I celebrate the joy of movement and the unity it brings. In the future, I aspire to bridge cultural gaps through the universal language of dance. Join me at the next event, and let's sway to the rhythm of friendship and shared experiences!"
    },
    'Laura Davis': {
        'student_id': 20240132,
        "bio": "Hola, queridos! I'm Laura Davis, a passionate university student with a heart set on exploration and cultural celebration. University events are my canvas for discovering new perspectives and building connections that transcend borders. As a proud member of the Photography Club, I capture moments that tell stories and celebrate the beauty of diversity. In the future, I dream of merging my love for photography with humanitarian efforts, using visuals to create awareness and inspire change. Join me at the next event, and let's capture memories that resonate through our university journey!"
    },
    'Amalia Taylor': {
        'student_id': 20240133,
        "bio": "Greetings, kindred spirits! I'm Amalia Taylor, a university dreamer weaving my story through the vibrant fabric of campus life. University events are my palette for self-expression and connecting with fellow dreamers. Embracing the world of music in the Music Club, I find solace and joy in the harmonies that unite us. In the future, I envision a career where I can infuse creativity into everyday life, leaving traces of inspiration wherever I go. Join me at the next event, and let's create melodies of friendship and shared experiences!"
    },
    'Marina Murphy': {
        'student_id': 20240134,
        "bio": "Hello, universe! I'm Marina Murphy, a university dreamer with a heart set on exploration and a love for diverse experiences. University events, with their dynamic energy, are my canvas for self-expression and connecting with fellow dreamers. Engaging in the world of debate in the Debate Club, I find joy in articulating ideas and engaging in thought-provoking discussions. In the future, I see myself advocating for positive change through the power of words. Join me at the next event, and let's debate, discuss, and create memories that shape our university journey!"
    },
}

courses = ['BS', 'DS', 'COMSCI', 'COMBUS', 'ACM']
for name, user_data in users_data.items():
    first_name, last_name = name.split()
    username = first_name.lower()
    user = User.objects.create_user(
        username=username,
        email=f'{username}@mail.dcu.ie',
        password=f'{first_name.capitalize()}12345',
        student_id=user_data["student_id"],
        first_name=first_name,
        last_name=last_name,
        user_type='user'
    )
    user.profile.birthday = timezone.now().date() - timedelta(days=random.randint(7000, 9000))
    user.profile.course = random.choice(courses)
    user.profile.year = random.randint(1, 5)
    user.profile.description = user_data["bio"]
    user.profile.verified = random.choice([True, False])
    user.profile.save()

clubs_data = {
    "clubs": [
        {
            "name": "Badminton Club",
            "description": "Smash, Rally, Triumph!",
            "content": "Welcome to the exhilarating world of the Badminton Club, where shuttlecocks soar and racquets clash in the pursuit of athletic excellence. Our club is a dynamic community that caters to badminton enthusiasts of all skill levels. Whether you're a seasoned player or a complete beginner, our friendly environment provides the perfect platform to hone your skills and connect with fellow shuttlecock enthusiasts.\n\nImmerse yourself in the thrill of our Smash Tournaments, where competitors showcase their finesse on the court. Join our Doubles Challenges to experience the synergy of teamwork and strategic play. Beginners are invited to embark on their badminton journey through engaging workshops, designed to introduce the basics and foster a love for the sport. Additionally, our Badminton Marathons and Mixed Doubles Mixers create a vibrant atmosphere of camaraderie, ensuring that every member feels a sense of belonging and sportsmanship. Join us in the fast-paced world of badminton, where every rally is a step towards personal growth and shared success."
        },
        {
            "name": "Debate Club",
            "description": "Speak, Persuade, Conquer!",
            "content": "Step into the world of articulate discourse with the Debate Club, where words become powerful instruments of change. Our club is a melting pot of ideas, providing a platform for students to express themselves, refine their public speaking skills, and engage in thought-provoking discussions. Whether you're an experienced debater or a novice exploring the art of rhetoric, we welcome you to join our vibrant community.\n\nParticipate in our Great Debate Nights, where minds collide in intellectual battles that leave lasting impressions. Hone your public speaking prowess in specialized workshops, designed to enhance your oratory skills and boost your confidence. Test your wit in Debating Championships that challenge your ability to think critically and articulate persuasive arguments. The Debate Club is more than just a forum; it's a community that fosters intellectual growth, encourages diverse perspectives, and empowers individuals to become effective communicators. Join us in shaping the leaders and changemakers of tomorrow through the power of words."
        },
        {
            "name": "Basketball Club",
            "description": "Dribble, Shoot, Soar!",
            "content": "Get ready to dribble, shoot, and slam dunk your way into the heart of the Basketball Club! Our club is a vibrant hub for basketball enthusiasts, where skill meets passion on the court. Whether you're a seasoned player or a rookie eager to embrace the game, our community welcomes all with open arms.\n\nExperience the adrenaline rush of our Slam Dunk Showcases, where players showcase their aerial prowess and hoop skills. Compete in our 3-on-3 Tournaments to test your teamwork and strategic play. Sharpen your basketball finesse in our skills clinics designed for players of all levels. March to the beat of Hoops for Charity, where the spirit of the game converges with philanthropy. The Basketball Club is more than just a sports club; it's a community that fosters teamwork, sportsmanship, and a shared love for the game. Join us and let the bouncing ball be the rhythm of your university journey."
        },
        {
            "name": "Investing Society",
            "description": "Invest Wisely, Prosper Boldly!",
            "content": "Welcome to the Investing Society, where financial literacy meets the excitement of the stock market. Our society is a hub for students interested in unlocking the secrets of smart investing, navigating the world of stocks, and making informed financial decisions. Whether you're a finance enthusiast or a novice eager to learn, the Investing Society provides the tools and knowledge you need to thrive.\n\nEngage in our Stock Market Challenge, a dynamic event that simulates real-world trading scenarios and hones your investment skills. Attend our Investment Seminars, where industry experts share insights into the world of finance. Dive into the excitement of our Trading Simulation Events, gaining hands-on experience in the fast-paced world of stock trading. The Investing Society is not just about numbers; it's about empowering students to achieve financial well-being, make informed decisions, and build a foundation for a secure future. Join us and embark on a journey towards financial mastery."
        },
        {
            "name": "Chess Club",
            "description": "Check. Mate. Elevate.",
            "content": "Enter the strategic realm of the Chess Club, where intellect meets competition in a battle of wits. Our club is a haven for chess enthusiasts, whether you're a seasoned grandmaster or a beginner eager to learn the intricacies of the game. Join our community to experience the timeless allure of chess and connect with like-minded individuals who share a passion for strategy.\n\nParticipate in Grandmaster Exhibitions, where seasoned players showcase their mastery of the game. Test your speed and strategy in our Speed Chess Tournaments, designed to challenge your quick thinking and tactical skills. Hone your strategic prowess in Chess Strategy Workshops, where experienced players share tips and techniques. Engage in Simultaneous Chess Challenges, a thrilling event where players face off against multiple opponents simultaneously. The Chess Club is not just about the game; it's about fostering a community of intellectual excitement, strategic thinking, and lifelong connections. Join us and make your move in the world of chess."
        },
        {
            "name": "Music Club",
            "description": "Harmony Unleashed, Notes Embraced!",
            "content": "Immerse yourself in the harmonious world of the Music Club, where melodies, rhythms, and creative expression converge to create unforgettable experiences. Our club is a diverse community that welcomes musicians, vocalists, and music enthusiasts of all skill levels. Join us to explore the limitless possibilities of musical expression and connect with a community that shares your love for music.\n\nParticipate in our Open Mic Nights, where talents take center stage in an atmosphere of creativity and support. Experience the energy of our Battle of the Bands, a showcase of musical prowess and eclectic genres. Hone your songwriting skills in our Songwriting Workshops, designed to inspire and guide aspiring musicians. Join our Acoustic Jam Sessions, where collaborative music-making becomes an immersive experience. The Music Club is not just about playing notes; it's about creating a harmonious community that celebrates diversity, creativity, and the joy of making music together. Join us and let the rhythm of music be the soundtrack to your university journey."
        },
        {
            "name": "Dance Club",
            "description": "Move, Groove, Unleash!",
            "content": "Step into the vibrant world of the Dance Club, where movement becomes a form of self-expression, and rhythm takes center stage. Our club is a dynamic community that welcomes dancers of all skill levels, from those with years of experience to those taking their first dance steps. Join us to explore various dance styles, connect with like-minded individuals, and let the joy of dance elevate your university experience.\n\nExperience the magic of our Dance Showcases, where choreography and performance create unforgettable moments. Hone your dance skills in our Dance Workshop Series, led by experienced instructors passionate about sharing their love for dance. Engage in exhilarating Choreography Battles, where creativity and expression collide. Join our Social Dance Nights to connect with fellow dancers and embrace the diversity of dance styles. The Dance Club is not just about movements; it's about building a community that celebrates the joy, expression, and unity that dance brings. Join us and let your dance journey unfold in rhythm and harmony."
        },
        {
            "name": "Art Club",
            "description": "Brush, Create, Inspire!",
            "content": "Unleash your creativity in the Art Club, canvas and imagination knows no bounds. Our club is a vibrant community that celebrates the diverse world of visual arts, welcoming artists of all levels to explore, create, and inspire.\n\nJoin us for Art Exhibitions, where creativity takes center stage and artworks come to life. Immerse yourself in Painting Workshops, where strokes on canvas become a form of personal expression. Engage in Sculpture Symposia, molding and shaping ideas into tangible art forms. Experience the thrill of Live Art Demonstrations, where artists showcase their techniques and share the magic of the creative process. Collaborate on Artistic Projects that merge individual visions into collective masterpieces. The Art Club is not just about creating art; it's about fostering a community that embraces diversity, encourages exploration, and finds beauty in every stroke. Join us and let your creativity flourish in the kaleidoscope of visual arts."
        },
        {
            "name": "Coding Club",
            "description": "Code, Collaborate, Innovate!",
            "content": "Unlock the language of the future with the Coding Club, where lines of code become a canvas for innovation and problem-solving. Our club is a dynamic community that welcomes coding enthusiasts, from seasoned developers to beginners eager to explore the world of programming.\n\nEngage in our Hackathons, where creativity meets coding speed in a race against the clock. Join our Coding Bootcamps, where intensive learning sessions turn novices into coding maestros. Explore the latest technologies in our Tech Talk Series, featuring industry experts and cutting-edge topics. Participate in Code Review Sessions to refine your skills and collaborate on real-world projects. Showcase your coding prowess in Algorithmic Coding Competitions that challenge your problem-solving abilities. The Coding Club is not just about writing code; it's about building a community that thrives on innovation, collaboration, and the endless possibilities of technology. Join us and let your code create the future."
        },
        {
            "name": "Photography Club",
            "description": "Capture Moments, Create Memories!",
            "content": "Capture the beauty of moments with the Photography Club, where lenses become storytellers and every click preserves a narrative. Our club is a diverse community that welcomes photographers of all skill levels, from seasoned professionals to those capturing their first frames.\n\nJoin us for Photo Walks and Shoots, where every corner becomes a canvas waiting to be explored. Showcase your skills in Photography Contests, celebrating the unique perspectives our members bring. Perfect your craft in Portrait Photography Workshops, capturing the essence of personalities in every frame. Dive into the world of visual storytelling with Photo Editing Masterclasses, where images transform into narratives. Share your vision in Photography Exhibitions, turning moments into timeless art. The Photography Club is not just about taking pictures; it's about creating a visual language that transcends boundaries, connects people, and immortalizes the beauty of fleeting moments. Join us and let your lens tell stories that last a lifetime."
        }
    ]
}

# # Club
for club_data in clubs_data["clubs"]:
    club = Club.objects.create(
        name=club_data["name"],
        description=club_data["description"],
        email=f'{club_data["name"].replace(" ", "").lower()}@dcu.ie',
        content=club_data["content"]
    )
    club_admins = random.sample(list(User.objects.all()), random.randint(1, 3))
    club.club_admins.add(*club_admins)

# # Event
club_event_titles = {
    'Badminton Club': ['Smash Tournament', 'Doubles Challenge', 'Beginners\' Workshop', 'Badminton Marathon', 'Mixed Doubles Mixer'],
    'Debate Club': ['Great Debate Night', 'Public Speaking Workshop', 'Debating Championship', 'Mock Trial Event', 'Impromptu Debate Session'],
    'Basketball Club': ['Slam Dunk Showcase', '3-on-3 Tournament', 'Basketball Skills Clinic', 'March Madness Viewing Party', 'Hoops for Charity'],
    'Investing Society': ['Stock Market Challenge', 'Financial Literacy Workshop', 'Investment Seminar', 'Portfolio Review Session', 'Trading Simulation Event'],
    'Chess Club': ['Grandmaster Exhibition', 'Speed Chess Tournament', 'Chess Strategy Workshop', 'Simultaneous Chess Challenge', 'Chess Open Championship'],
    'Music Club': ['Open Mic Night', 'Battle of the Bands', 'Songwriting Workshop', 'Acoustic Jam Session', 'Music Appreciation Night'],
    'Dance Club': ['Dance Showcase', 'Dance Workshop Series', 'Choreography Battle', 'Social Dance Night', 'Flash Mob Event'],
    'Art Club': ['Art Exhibition', 'Painting Workshop', 'Sculpture Symposium', 'Live Art Demonstration', 'Artistic Collaboration Project'],
    'Coding Club': ['Hackathon', 'Coding Bootcamp', 'Tech Talk Series', 'Code Review Session', 'Algorithmic Coding Competition'],
    'Photography Club': ['Photo Walk and Shoot', 'Photography Contest', 'Portrait Photography Workshop', 'Photo Editing Masterclass', 'Photography Exhibition']
}

locations = ['The Hive', 'DCU Gym', 'DCU labs', 'The Venue at DCU']
event_types = [choice[0] for choice in Event.EVENT_CHOICES]
for club in Club.objects.all():
    event_titles = club_event_titles[club.name]
    for title in event_titles:
        event = Event.objects.create(
            title=title,
            description=f'This is {title}. Join us for a great time!',
            price=0,
            date=timezone.now().date() + timedelta(days=random.randint(30, 365)),
            time=timezone.now().time(),
            capacity=random.randint(5, 40),
            soldout=False,
            location=random.choice(locations),
            event_type=random.choice(event_types),
            club=club
        )

# # Friend
users = list(User.objects.all())
for user in users:
    friends = random.sample([u for u in users if u != user], random.randint(0, 15))
    for friend in friends:
        Friend.objects.create(
            sender=user,
            receiver=friend,
            status=random.choice([True, False])
        )

# Follow
for user in users:
    clubs = random.sample(list(Club.objects.all()), random.randint(1, 6))
    for club in clubs:
        Follow.objects.create(user=user, club=club)

# Ticket
for user in users:
    events = random.sample(list(Event.objects.all()), random.randint(1, 7))
    for event in events:
        if Ticket.objects.filter(event=event).count() < event.capacity:
            # Create the ticket without the QR code
            ticket = Ticket.objects.create(
                title=event.title,
                code=ticketCodeGenerator(),
                price=event.price,
                status='A',
                user=user,
                event=event
            )
            # Generate the QR code using the ticket ID
            qr_code_image = ticketQRCodeGenerator(ticket.id)
            ticket.qr_code.save(f"ticket_{ticket.id}_qr_code.png", ContentFile(qr_code_image.getvalue()))
            ticket.save()