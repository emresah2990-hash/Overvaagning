# Overvågningssystem

Et lille personligt projekt, jeg lavede for selv at holde øje med, om tingene i mit netværk – som min router og PC – rent faktisk er tændt og svarer. Samtidig var det en god undskyldning for at lære Azure DevOps ordentligt at kende.

## Hvad gør det?

Scriptet tjekker med jævne mellemrum, om en liste af hosts svarer (via ping eller HTTP). Går noget ned – eller kommer op igen – sender det automatisk en mail, så jeg ved det med det samme.

## Hvordan hænger det sammen?

- **Python** står for selve overvågningslogikken
- **Gmail** sender alarmerne
- **systemd** holder scriptet kørende i baggrunden på en Ubuntu-VM, døgnet rundt
- **Azure DevOps** binder det hele sammen: koden ligger i Repos, opgaverne i Boards, og en pipeline tester og udruller automatisk koden, hver gang jeg ændrer noget

## Kom i gang

```bash
pip install -r requirements.txt
```

Ret dine egne hosts og Gmail-oplysninger i `config.yaml`, og kør:

```bash
python3 monitor.py
```

Nysgerrig på automatiseringen? Kig i `azure-pipelines.yml` (CI/CD) og `overvaagning.service` (baggrundskørsel).
