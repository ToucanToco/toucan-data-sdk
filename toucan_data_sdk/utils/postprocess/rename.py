from typing import Dict


def _safe_translate(translations, locale, fallback_locale='en', default=None):
    """return `locale` translation from `translations`.

    Fallback on `fallback_locale` if `locale` translation can't be found and
    eventually fallback on `default` is none of the locales translations can't
    be found.
    """
    if locale in translations:
        return translations[locale]
    if fallback_locale in translations:
        return translations[fallback_locale]
    return default


def rename(
    df,
    values: Dict[str, Dict[str, str]] = None,
    columns: Dict[str, Dict[str, str]] = None,
    locale: str = None,
    fallback_locale='en',
):
    """
    Replaces data values and column names according to the locale

    ---

    ### Parameters

    - `values` (optional: dict):
        - key: term to be replaced
        - value:
            - key: the locale e.g. 'en' or 'fr'
            - value: term's translation
    - `columns` (optional: dict):
        - key: columns name to be replaced
        - value:
            - key: the locale e.g. 'en' or 'fr'
            - value: column name's translation
    - `locale` (optional: str): the locale you want to use.
      By default the client locale is used.

    - fallaback_locale (str): default locale in `locale` can't be found.
      If none of the locales can't be found, it will default on untranslated
      values.

    ---

    ### Example

    **Input**

    | label | value |
    |:----------------:|:-----:|
    | France | 100 |
    | Europe wo France | 500 |

    ```cson
    rename:
      values:
        'Europe wo France':
          'en': 'Europe excl. France'
          'fr': 'Europe excl. France'
      columns:
        'value':
          'en': 'revenue'
          'fr': 'revenue'
    ```

    **Output**

    | label | revenue |
    |:-------------------:|:-------:|
    | France | 100 |
    | Europe excl. France | 500 |

    """
    if values:
        to_replace = list(values.keys())
        value = [
            _safe_translate(values[term], locale, fallback_locale, default=term) for term in values
        ]
        df = df.replace(to_replace=to_replace, value=value)
    if columns:
        columns = {
            k: _safe_translate(v, locale, fallback_locale, default=k) for k, v in columns.items()
        }
        df = df.rename(columns=columns)
    return df
