# CheckCanyonBikeAvailability

CheckCanyonBikeAvailability is a telegramm bot to check the availability of one or more canyon bikes on their website.

# Requirement 

- Python3

# Setup

## Create Virtual Environment

The virtual environment is not necessary but resolve most problem with packages requirements conflict. For more info see the 
[official guide](https://docs.python.org/3/tutorial/venv.html).

For create new virtual environment open new terminal in this project and type this command:

``` 
python3 -m venv venv
```

The second ``venv`` is the name of new virtual environment.

Once you’ve created a virtual environment, you may activate it.

On Windows, run:

```
venv\Scripts\activate.bat
```

On Unix or MacOS, run:

```
source venv/bin/activate
```

Activating the virtual environment will change your shell’s prompt to show what virtual environment you’re using, and modify the environment so that running python will get you that particular version and installation of Python.

## Install Python Requirement

```
pip install -r requirements.txt
```

# Configuration

On file config.json setup your telegram `userid` and your `token` given by botfather.

:exclamation: Attention 

Sometimes the canyon site is updated and you have to look for the css classes and html tags and write them in the config file.


# Run

```python3 main.py```

# Usage

Bot commands:

- **/list** to see the list of bikes to check
- **/add** to add new bike to check 
- **/remove** to remove a bike from the list


if you want to add bikes manually you can do it using the ``bike.json`` file as in the following example

```
{
  "bikes": {
    "torque": {
      "link": "https://www.canyon.com/it-it/mountain-bikes/enduro-bikes/torque/al/torque-6/2666.html?dwvar_2666_pv_rahmenfarbe=BK%2FGY",
      "size": "M"
    },
    "spectral": {
      "link": "https://www.canyon.com/it-it/mountain-bikes/trail-bikes/spectral/spectral-27-5/spectral-6/2675.html?dwvar_2675_pv_rahmenfarbe=BK%2FGY",
      "size": "M"
    }
  }
}
```

For bot log check ``log.txt`` file.