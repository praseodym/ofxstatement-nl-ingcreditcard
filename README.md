# ofxstatement plugin for Dutch ING Creditcard

This is a [ofxstatement] plugin for ING Creditcard in The Netherlands.

Unfortunately ING does not provide exports for creditcard statements in the
'Mijn ING' environment. This plugin extracts the transactions from a [HAR file]
containing the 'Mijn ING' HTTP requests and responses with your creditcard transactions.

After [installing this plugin][plugin-howto], create a HAR file from your ING Creditcard
transactions to convert it to OFX.

The general steps to create a HAR file in Firefox are:

1. Log in to 'Mijn ING'
2. Open Developer Tools with `F12`
3. Open your creditcard statement in 'Mijn ING' and load transactions
   in previous periods as needed
4. In the Developer Tools' Network panel, click the 'Network Settings'
   (cogwheel) on the top right and 'Save All As HAR'
5. Run ofxstatement:
   `ofxstatement convert -t ingcreditcard [input HAR filename] [output OFX filename]`

If needed, [more detailed instructions can be found on the web][ddg-har].

[ofxstatement]: https://github.com/kedder/ofxstatement
[HAR file]: https://en.wikipedia.org/wiki/HAR_(file_format)
[plugin-howto]: https://github.com/kedder/ofxstatement#installation-and-usage
[ddg-har]: https://duckduckgo.com/?q=create+har+file "How to create a HAR file"