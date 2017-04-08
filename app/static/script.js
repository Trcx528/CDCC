function filterContacts() {
    var orgId = $("#Organization").val();
    var flag = false;
    var options = $('#Contact > option');
    for (var i=0; i<options.length; i++) {
        var data = orgData[orgId];
        if (options[i].value in data) {
            $(options[i]).show();
            $(options[i]).removeAttr('disabled');
            $(options[i])
            if (!flag){
                flag=true;
                if (!($('#Contact').val() in data)) {
                    $('#Contact').val(options[i].value);
                }
            }
        } else {
            $(options[i]).hide();
            //set the disabled attr as a fall back
            $(options[i]).attr('disabled','disabled');
        }
    }
}

function currency(x) {
    return x.toFixed(2).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function updateCaterering() {
    var cTotal = 0;
    var dInput = $('.dish-input');
    for(var i=0; i<dInput.length; i++){
        var total = dInput[i].dataset.price * dInput[i].value;
        cTotal += total;
        $('#' + dInput[i].name.replace('dish_', '') + '_total').html('$' + currency(total));
    }
    $('#catereringTotal').html('$' + cTotal.toFixed(2));
    $('#catereringTotal').addClass('to-total');
    $('#catereringTotal').data('total', cTotal);
    updateTotal();
}

function updateTotal() {
    var subTotal = 0;
    var totals=$('.to-total');
    for (var i=0; i<totals.length; i++){
        console.log(totals[i].id, $(totals[i]).data('total'));
        subTotal += $(totals[i]).data('total');
    };
    $('#subtotal').html('$' + currency(subTotal));
    var finalDiscountAmount = getDiscount(subTotal);
    console.log('Discount ' + finalDiscountAmount);
    $('#discountTotal').html('$' + currency(finalDiscountAmount));
    $('#finalTotal').html('$' + currency(subTotal - finalDiscountAmount));
}


function getDiscount(subTotal) {
    //return ((self.subTotal() - self.discountAmount) * self.discountPercent/100) + self.discountAmount
    var dPer = parseFloat($('#DiscountPercent').val());
    var dAmt = parseFloat($('#DiscountAmount').val());
    return ((subTotal - dAmt) * dPer/100) + dAmt
}