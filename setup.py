import setuptools
from instapy_bot.version import Version


setuptools.setup(name="instapy_bot",
                 version=Version("0.1.1").number,
                 description="Python instagram automated uploader",
                 long_description=open("README.md").read().strip(),
                 author="Nikola Tasic",
                 author_email="ntasic7@gmail.com",
                 url="http://github.com/7aske/instapy-bot",
                 py_modules=["instapy_bot"],
                 install_requires=["pillow", "requests"],
                 license="MIT License",
                 zip_safe=False,
                 keywords="python instagram bot",
                 entry_points={
                     "console_scripts": ["instapy-cli=instapy_bot.cli.__main__:main",
                                         "instapy-bot=instapy_bot.bot.__main__:main"],
                 })
