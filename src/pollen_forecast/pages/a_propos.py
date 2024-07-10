"""Generate the about page of the app."""
import streamlit as st

ABOUT_TEXT = """
# Prévision du pollen

L'objectif de ce site est de visualiser la prévision du pollen pour une ville donnée en France.

Il utilise les données de [Copernicus](https://ads.atmosphere.copernicus.eu/cdsapp#!/dataset/cams-europe-air-quality-forecasts?tab=overview).
Les valeurs affichées correspondent à la médianes de differentes simulations.

Les données sont disponibles chaque jour à 8h pour la journée en cours et les 4 jours suivants.

## Mise en garde
Ce site est en cours de développement, il peut y avoir des erreurs dans les prévisions affichées.

Pour des données plus fiables, vous pouvez consulter le site de [RNSA](https://pollens.fr/).

## Contact

Pour toute question ou suggestion, vous pouvez me contacter par mail à l'adresse suivante: antoinetavant at hotmail.fr


-----------

Developpé avec ❤️ avec [Streamlit](https://streamlit.io/), [Altair](https://altair-viz.github.io/) et [Xarray](http://xarray.pydata.org/en/stable/) par [Antoine Tavant](https://github.com/antoinetavant) - 2024
"""
def a_propos():
    """display the about page"""
    st.markdown(ABOUT_TEXT)

if __name__ == "__main__":
    a_propos()
