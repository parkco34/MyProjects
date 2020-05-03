function incrementor(amount, i) {
    var collxn = document.getElementsByClassName('amount');
    var amnt = parseInt(document.getElementById(amount).value);
    if (collxn[i].getAttribute('value') == "increase") {
        amnt++;
    }
    else if (collxn[i].getAttribute('value') == "decrease") {
        if (amnt >= 1) {
            amnt--;
        }
    }
    document.getElementById(amount).value = amnt;
    return amnt;
}
function total(dollas, qty, totals) {
    var costString = document.getElementById(dollas).innerHTML,
        cost = parseFloat(costString.substring(1));
    if (Number.isNaN(cost)) {
        var costString = document.getElementById(dollas).value,
            cost = parseFloat(costString),
            numberOfItems = parseInt(document.getElementById(qty).value),
            itemTotal = (cost * numberOfItems).toFixed(2);
        document.getElementById(totals).innerHTML = '$ ' + itemTotal;
    }
    else {
        var numberOfItems = parseInt(document.getElementById(qty).value),
            itemTotal = (cost * numberOfItems).toFixed(2),
            itemTotal = itemTotal.toString();
        document.getElementById(totals).innerHTML = '$ ' + itemTotal;
    }
    return itemTotal;
}
function clearDaShit(qty, totals) {
    document.getElementById(qty).value = '0';
    document.getElementById(totals).innerHTML = '';
}

function getSubTotal() {
    var arr = Array();
    for (i = 1; i <= (document.getElementsByClassName('price').length); i++) {
        if (isNaN(parseFloat(document.getElementById('totals' + i.toString()).innerHTML.substring(1)))) {
            continue;
        }
        arr[i - 1] = parseFloat((document.getElementById('totals' + i.toString()).innerHTML.substring(1)));
    }
    let subtotal = (arr.reduce((x, y) => x + y, 0)).toFixed(2);
    document.getElementById('subtotal').innerHTML = '$ ' + subtotal.toString();
}

function grand() {
    let total_i = parseFloat(document.getElementById('subtotal').innerHTML.substring(1));
    total = (total_i + total_i * .08).toFixed(2);
    document.getElementById('grandtotal').innerHTML = '$ ' + total.toString();
}

function clearAll() {
    let quantity = document.querySelectorAll('.myForm');
    let totals = document.querySelectorAll('.actualprice');
    document.getElementById('cost2').value = "";
    for (i = 1; i <= document.getElementsByClassName('price').length; i++) {
        if (document.getElementById('totals' + i.toString()) != "" || document.getElementById('totals' + i.toString()) != "&nbsp;") {
            document.getElementById('totals' + i.toString()).innerHTML = "&nbsp;";
        }
        quantity[i - 1].reset();
    }

    document.getElementById('subtotal').innerHTML = "&nbsp;";
    document.getElementById('grandtotal').innerHTML = "&nbsp;";
}

