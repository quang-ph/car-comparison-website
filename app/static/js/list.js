function CreateProductItem(id,title,image,year){
    var mainDiv = $('<div>').attr('class','col-md-3 col-xs-6');
	var product = $('<div>').attr('class','product');
	var productImg = $('<div>').attr('class','product-img');
	var img = $('<img>').attr({'src':'../static/img/product01.png','data-holder-rendered':true});
	var productBody = $('<div>').attr('class','product-body');
	var productName = $('<h3>').attr('class','product-name');
	var productButton = $('<div>').attr('class','product-btns')
	var btn_wish = $('<button>').attr('class','add-to-wishlist')
	var btn_compare = $('<button>').attr('class','add-to-compare')
	var btn_quick_view = $('<button>').attr('class','quick-view')
	var view_product = $('<div>').attr('class','add-to-cart')

	productButton.append(btn_wish);
	productButton.append(btn_quick_view);
	productButton.append(product);
	productBody.append(productName);
	productBody.append(productButton);
	productImg.append(img)
	product.append(productImg);
	product.append(productBody);
	product.append(view_product)
	mainDiv.append(product);
	return mainDiv;}
