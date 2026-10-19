"""Restore written Rust names after the provider expands underscores for speech."""
import re
ALIASES={'map err':'map_err','strong count':'strong_count','macro rules':'macro_rules!','all targets':'--all-targets','assert eq':'assert_eq!','assert ne':'assert_ne!','should panic':'should_panic','into iter':'into_iter','iter mut':'iter_mut','borrow mut':'borrow_mut'}
def display_caption(text):
    for spoken,written in ALIASES.items():
        text=re.sub(r'(?<![A-Za-z])'+re.escape(spoken)+r'(?![A-Za-z])',lambda _:written,text,flags=re.I)
    return text
