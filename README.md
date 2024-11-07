
# 17lands Draft Notifier

Process 17lands logs for draft packs and print card ratings to stdout.

## Usage

```
> 17lands-draft-notifier <ratings> <ids> [[--ratings-column <colname>]...]

Arguments:
    ratings:
        Path to CSV file containing card ratings data. This should be exported 
        from the 17lands card data page.
        (https://www.17lands.com/card_data)

    ids:
        Path to CSV file containing card IDs. This can be scraped from the same
        card data page, using the dev tools in your browser.

Options:
    --ratings-column, -r:
        Column name(s) for rating values to sort on and display.
        Default: ["GIH WR"]
        Can specify multiple times to sort on multiple columns. Order matters. You may prefix a column name with a "-" to sort in ascending order.
```

## Setup

### ratings.csv

You will need to export the card ratings CSV file from the [17lands card data
page](https://www.17lands.com/card_data) for the expansion and format that you
are playing.

### ids.csv

You will also need to scrape a CSV of the Arena card IDs from the
same page. To do so open the dev tools in your browser, and run the following:
in the console.

> _*NB: IF YOU DO NOT KNOW WHAT YOU ARE DOING NEVER PASTE CODE INTO YOUR BROWSER'S CONSOLE!!!*_

```js
> idsCSV = ['"Name","CardID"'];
> document.querySelectorAll('a.list_card_name').forEach(a => idsCSV.push(`"${a.innerHTML}",${new URL(a.href).searchParams.get("card_id")}`))
> console.log(idsCSV.join('\n'))
```

Copy the output into a file on your computer.

## Examples

Basic usage:

```
> pipx run seventeenlands 2>&1  |
    17lands-draft-notifier ratings.csv ids.csv \
        --ratings-column "GIH WR" -r "GP WR" -r='IWD' -r="-ALSA"
```
