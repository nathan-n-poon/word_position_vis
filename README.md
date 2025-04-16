I'm using LibreOffice so closed source can't peddle my writing to some Butlerian proscribed entity.  
Sometimes when I write I forgor (when I last)||(how frequently) I use a term、 punctuation mark、 etc... and I want to avoid repetition and genericism.  
So I search for that term、 punctuation mark、 etc... and see if (the last usage is too proximate to my new intended site)||(it is generally overused).
However, LibreOffice (AFAIK, gave up after a DuckDuckGo search) doesn't display all occurrences of a search term across the span of a document, such as how chrome does along the scrollbar (example pic below)
![screenshot of chrome highlighting all occurrences of a search token (labor) along the scrollbar](img/Chrome_example.png "Reference impl")
This tool shows the occurrences of a search term per chapter

This tool crafted without:
- Enough sleep
- Sufficient principle
- Butlerian proscribed entities

TODO:
- chapter labels (easy)
- rn the textinput has default behaviour where either \<ENTER\> or \<clicking away from textinput\> triggers the callback. <br>  I would like it to only be on \<ENTER\>, as rn it will most likely cause one redundant callback invocation >:(
- update this README
- have toggles for Whole Word search and Match Case search (idk how difficult it is for allow regex search)
- have viewmode where camera moves to each search hit in sequence (probably involved), user can switch between free pan and this new mode
- maybe have a unified mode rather than broken down by chapter (this will be ugly probably)
- support odt