# design_capital_gains_page

This code is currently designated for the use of Israeli accountants (by choise).
I am working on a code that would fit internationally.

For accountants using the website Bitcoin.tax :
the website provides a set capital gain results. ( profit/loss)
These results needs to be assembled to an official form, each accountant would reflect his own regulatury requirments in its presentation and forward it with all tax files handed over to the authorities on the behalf of his clients.

presenting the main problem this code helps with:

Tax authorities work to distiguish between citizens who traded randomly (as a hobby) - their profits shall be regarded as "Capital Gains",
whereas those trading for a living (work) - their profits shall be regarded as "Income".
The overall tax result is straight forward different between these two options, and no one answer can be better in all cases,
you must reach out to your accountant and conduct a full investigation to understand this better.

In general, IRS and similar authorities would realize and determine to which status does the individual/company falls, mainly by observing the sheer number of profit lines they are given in the financial statements (individual/company).

In cases (to be honest, most cases) where it is preffered to have "Capital Gains" rather then "Income", we would normally want to minimize the size of our overall trading output as it is presented.

This code helps with just that.

Groupby By "sell date" your BitcoinTaxes's "Capital Gains output" and run it through this code to "shrink" the overall lines in the report to IRS, all that without misleading or presenting false information.

Available to give any assistance.

## Feb 2020 update

Software was updated so that it will contain updated currency rates and that it would be possible to make an executable out of it. 
The .exe can be generated using the auto-py-to-exe app, and the suitable config file is a .json file in this folder.

## June 2020 update

I had to modify the source code of pandas to make the templating thing work. The modification is done in `C:\Users\Ronit\AppData\Local\pypoetry\Cache\virtualenvs\capital-gains-designer-OfdUtgwm-py3.8\Lib\site-packages\pandas\io\formats\style.py` and it replaces `loader = ...` with: 
```
    if getattr(sys, 'frozen', False):
        # we are running in a bundle
        bundle_dir = sys._MEIPASS
        loader = jinja2.FileSystemLoader(bundle_dir)
    else:
        loader = jinja2.PackageLoader("pandas", "io/formats/templates")
```