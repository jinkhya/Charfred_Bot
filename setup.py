from setuptools import setup, find_packages

setup(
    name="Charfred",
    version="1.0alpha1",
    packages=find_packages(),
    install_requires=[
        'discord.py',
        'coloredlogs',
        'ttldict',
        'psutil',
        'pyfiglet',
        'click'],
    dependency_links=[
        'git+https://github.com/Rapptz/discord.py@rewrite#egg=discord.py'
    ],
    package_data={
        '': ['*.json', '*.json_default']
    },
    author="Kella",
    author_email="kellador@gmail.com",
    description="Charfred is a modular Discord bot with capabilities to manage your minecraft servers.",
    keywords="discord-bot discord.py minecraft minecraft-administration",
    entry_points={
        'console_scripts': [
            'charfred = charfred:run',
            'charwizard = charwizard:wizard',
            'spiffy = spiffy:spiffy'
        ]
    }
)
