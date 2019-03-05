$().ready(function () {

    let cart = 0;

    $("#tadimlik").click(function () {
        if(!$(this).hasClass("green")){$(this).toggleClass("blue").toggleClass("green");}
        switch (cart) {
            case 3:
                $("#merakli").toggleClass("blue").toggleClass("green");
                break;
            case 5:
                $("#bagimli").toggleClass("blue").toggleClass("green");
                break;
        }
        $("#buy-button").removeClass("disabled");
        cart = 1;
    });

    $("#merakli").click(function () {
        if(!$(this).hasClass("green")){$(this).toggleClass("blue").toggleClass("green");}
        switch (cart) {
            case 1:
                $("#tadimlik").toggleClass("blue").toggleClass("green");
                break;
            case 5:
                $("#bagimli").toggleClass("blue").toggleClass("green");
                break;
        }
        $("#buy-button").removeClass("disabled");
        cart = 3;
    });

    $("#bagimli").click(function () {
        if(!$(this).hasClass("green")){$(this).toggleClass("blue").toggleClass("green");}
        switch (cart) {
            case 1:
                $("#tadimlik").toggleClass("blue").toggleClass("green");
                break;
            case 3:
                $("#merakli").toggleClass("blue").toggleClass("green");
                break;
        }
        $("#buy-button").removeClass("disabled");
        cart = 5;
    });

    $("#buy-button").click(function () {
        $(this).addClass("disabled");
        $(".fa-spinner").show();
        $.ajax({
			url:'/buy/done',
			type:'POST',
			data:{"buy": cart},
			success:function(data){

                if(data.success === true){
                    swal({
                            buttonsStyling: false,
                            confirmButtonText: "Tamam",
                            confirmButtonClass: "btn green",
                            title: "Sipariş Alındı!",
                            html: `Sipariş kodunuz: ${data.SP} <br>Havale/EFT yapmanız gereken tutar: ${data.price}<br><small>Sipariş kodunuzu havale/EFT açıklama kısmına yazmayı unutmayın!</small>`,
                            type: "success"
                    }).then(function () {
                        $(".fa-spinner").hide();
                        // $("#buy-button").removeClass("disabled")
                    });
                }

			}
		});
    })
});