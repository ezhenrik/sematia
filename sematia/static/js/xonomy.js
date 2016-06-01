var Xonomy={
	lang: "", //"en"|"de"|fr"| ...
};

Xonomy.xmlEscape=function(str) {
    return String(str)
		.replace(/&/g, '&amp;')
		.replace(/"/g, '&quot;')
		.replace(/'/g, '&apos;')
		.replace(/</g, '&lt;')
		.replace(/>/g, '&gt;');
};
Xonomy.xmlUnscape=function(value){
    return String(value)
        .replace(/&quot;/g, '"')
        .replace(/&#39;/g, "'")
        .replace(/&lt;/g, '<')
        .replace(/&gt;/g, '>')
        .replace(/&amp;/g, '&');
};
Xonomy.isNamespaceDeclaration=function(attributeName) {
	//Tells you whether an attribute name is a namespace declaration.
	var ret=false;
	if(attributeName=="xmlns") ret=true;
	if(attributeName.length>=6 && attributeName.substring(0, 6)=="xmlns:") ret=true;
	return ret;
};
Xonomy.namespaces={}; //eg. "xmlns:mbm": "http://lexonista.com"

Xonomy.xml2js=function(xml, jsParent) {
	if(typeof(xml)=="string") xml=$.parseXML(xml);
	if(xml.documentElement) xml=xml.documentElement;
	var js=new Xonomy.surrogate(jsParent);
	js.type="element";
	js.name=xml.nodeName;
	js.htmlID="";
	js.attributes=[];
	for(var i=0; i<xml.attributes.length; i++) {
		var attr=xml.attributes[i];
		if(!Xonomy.isNamespaceDeclaration(attr.nodeName)) {
			js["attributes"].push({type: "attribute", name: attr.nodeName, value: attr.value, htmlID: ""});
		} else {
			Xonomy.namespaces[attr.nodeName]=attr.value;
		}
	}
	js.children=[];
	for(var i=0; i<xml.childNodes.length; i++) {
		var child=xml.childNodes[i];
		if(child.nodeType==1) { //element node
			js["children"].push(Xonomy.xml2js(child, js));
		}
		if(child.nodeType==3) { //text node
			js["children"].push({type: "text", value: child.nodeValue, htmlID: ""});
		}
	}
	js=Xonomy.enrichElement(js);
	return js;
};
Xonomy.js2xml=function(js) {
	var xml="<"+js.name;
	for(var i=0; i<js.attributes.length; i++) {
		var att=js.attributes[i];
		xml+=" "+att.name+"='"+Xonomy.xmlEscape(att.value)+"'";
	}
	if(js.children.length>0) {
		xml+=">";
		for(var i=0; i<js.children.length; i++) {
			var child=js.children[i];
			if(child.type=="text") xml+=Xonomy.xmlEscape(child.value); //text node
			else if(child.type=="element") xml+=Xonomy.js2xml(child); //element node
		}
		xml+="</"+js.name+">";
	} else {
		xml+="/>";
	}
	return xml;
};
Xonomy.enrichElement=function(jsElement) {
	jsElement.hasAttribute=function(name) {
		var ret=false;
		for(var i=0; i<this.attributes.length; i++) {
			if(this.attributes[i].name==name) ret=true;
		}
		return ret;
	};
	jsElement.getAttributeValue=function(name, ifNull) {
		var ret=ifNull;
		for(var i=0; i<this.attributes.length; i++) {
			if(this.attributes[i].name==name) ret=this.attributes[i].value;
		}
		return ret;
	};
	jsElement.hasChildElement=function(name) {
		var ret=false;
		for(var i=0; i<this.children.length; i++) {
			if(this.children[i].name==name) ret=true;
		}
		return ret;
	};
	return jsElement;
};

Xonomy.verifyDocSpec=function() { //make sure the docSpec object has everything it needs
	if(!Xonomy.docSpec || typeof(Xonomy.docSpec)!="object") Xonomy.docSpec={};
	if(!Xonomy.docSpec.elements || typeof(Xonomy.docSpec.elements)!="object") Xonomy.docSpec.elements={};
	if(!Xonomy.docSpec.onchange || typeof(Xonomy.docSpec.onchange)!="function") Xonomy.docSpec.onchange=function(){};
	if(!Xonomy.docSpec.validate || typeof(Xonomy.docSpec.validate)!="function") Xonomy.docSpec.validate=function(){};
};
Xonomy.asFunction=function(specProperty, defaultValue){
	if(typeof(specProperty)=="function")
		return specProperty;
	else if (typeof(specProperty)==typeof(defaultValue))
		return function() { return specProperty; }
	else
		return function() { return defaultValue };
}
Xonomy.verifyDocSpecElement=function(name) { //make sure the DocSpec object has such an element, that the element has everything it needs
	if(!Xonomy.docSpec.elements[name] || typeof(Xonomy.docSpec.elements[name])!="object") Xonomy.docSpec.elements[name]={};
	var spec=Xonomy.docSpec.elements[name];
	if(!spec.attributes || typeof(spec.attributes)!="object") spec.attributes={};
	if(!spec.menu || typeof(spec.menu)!="object") spec.menu=[];
	if(!spec.inlineMenu || typeof(spec.inlineMenu)!="object") spec.inlineMenu=[];
	if(!spec.canDropTo || typeof(spec.canDropTo)!="object") spec.canDropTo=[];
	if(!spec.mustBeAfter || typeof(spec.mustBeAfter)!="object") spec.mustBeAfter=[];
	if(!spec.mustBeBefore || typeof(spec.mustBeBefore)!="object") spec.mustBeBefore=[];
	spec.oneliner=Xonomy.asFunction(spec.oneliner, false);
	spec.hasText=Xonomy.asFunction(spec.hasText, false);
	spec.collapsed=Xonomy.asFunction(spec.collapsed, false);
	for(var i=0; i<spec.menu.length; i++) Xonomy.verifyDocSpecMenuItem(spec.menu[i]);
	for(var i=0; i<spec.inlineMenu.length; i++) Xonomy.verifyDocSpecMenuItem(spec.inlineMenu[i]);
};
Xonomy.verifyDocSpecAttribute=function(elementName, attributeName) { //make sure the DocSpec object has such an attribute, that the attribute has everything it needs
	var elSpec=Xonomy.docSpec.elements[elementName];
	if(!elSpec.attributes[attributeName] || typeof(elSpec.attributes[attributeName])!="object") elSpec.attributes[attributeName]={};
	var spec=elSpec.attributes[attributeName];
	if(!spec.asker || typeof(spec.asker)!="function") spec.asker=function(){return ""};
	if(!spec.menu || typeof(spec.menu)!="object") spec.menu=[];
	for(var i=0; i<spec.menu.length; i++) Xonomy.verifyDocSpecMenuItem(spec.menu[i]);
};
Xonomy.verifyDocSpecMenuItem=function(menuItem) { //make sure the menu item has all it needs
	if(!menuItem.caption) menuItem.caption="?";
	if(!menuItem.action || typeof(menuItem.action)!="function") menuItem.action=function(){};
	if(!menuItem.hideIf) menuItem.hideIf=function(){return false;};
};

Xonomy.nextID=function() { 
	return "xonomy"+(++Xonomy.lastIDNum);
};
Xonomy.lastIDNum=0;

Xonomy.docSpec=null;
Xonomy.refresh=function() {
	$(".xonomy .children ").each(function(){ //determine whether each element does or doesn't have children:
		if(this.childNodes.length==0 && !$(this.parentNode).hasClass("hasText")) $(this.parentNode).addClass("noChildren");
		else {
			$(this.parentNode).removeClass("noChildren");
			Xonomy.updateCollapsoid(this.parentNode.id);
		}
	});
	var merged=false; while(!merged) { //merge adjacent text nodes
		merged=true; var textnodes=$(".xonomy .textnode").toArray();
		for(var i=0; i<textnodes.length; i++) {
			var $this=$(textnodes[i]);
			if($this.next().hasClass("textnode")) {
				var js1=Xonomy.harvestText($this.toArray()[0]);
				var js2=Xonomy.harvestText($this.next().toArray()[0]);
				js1.value+=js2.value;
				$this.next().remove();
				$this.replaceWith(Xonomy.renderText(js1));
				merged=false;
				break;
			}
		}
	}
	$(".xonomy .element ").each(function(){ //reorder elements if necessary
		var elSpec=Xonomy.docSpec.elements[this.getAttribute("data-name")];
		if(elSpec.mustBeBefore) { //is it after an element it cannot be after? then move it up until it's not!
			var $this=$(this);
			var ok; do {
				ok=true;
				for(var ii=0; ii<elSpec.mustBeBefore.length; ii++) {
					if( $this.prevAll("*[data-name='"+elSpec.mustBeBefore[ii]+"']").toArray().length>0 ) {
						$this.prev().before($this);
						ok=false;
					}
				}
			} while(!ok)
		}
		if(elSpec.mustBeAfter) { //is it before an element it cannot be before? then move it down until it's not!
			var $this=$(this);
			var ok; do {
				ok=true;
				for(var ii=0; ii<elSpec.mustBeAfter.length; ii++) {
					if( $this.nextAll("*[data-name='"+elSpec.mustBeAfter[ii]+"']").toArray().length>0 ) {
						$this.next().after($this);
						ok=false;
					}
				}
			} while(!ok)
		}
	});
	$(".xonomy .attribute ").each(function(){ //reorder attributes if necessary
		var atName=this.getAttribute("data-name");
		var elName=this.parentNode.parentNode.parentNode.getAttribute("data-name");
		var elSpec=Xonomy.docSpec.elements[elName];
		var mustBeAfter=[]; for(var sibName in elSpec.attributes) {
			if(sibName==atName) break; else mustBeAfter.push(sibName);
		}
		var mustBeBefore=[]; var seen=false; for(var sibName in elSpec.attributes) {
			if(sibName==atName) seen=true; else if(seen) mustBeBefore.push(sibName);
		}
		if(mustBeBefore.length>0) { //is it after an attribute it cannot be after? then move it up until it's not!
			var $this=$(this);
			var ok; do {
				ok=true;
				for(var ii=0; ii<mustBeBefore.length; ii++) {
					if( $this.prevAll("*[data-name='"+mustBeBefore[ii]+"']").toArray().length>0 ) {
						$this.prev().before($this);
						ok=false;
					}
				}
			} while(!ok)
		}
		if(mustBeAfter.length>0) { //is it before an attribute it cannot be before? then move it down until it's not!
			var $this=$(this);
			var ok; do {
				ok=true;
				for(var ii=0; ii<mustBeAfter.length; ii++) {
					if( $this.nextAll("*[data-name='"+mustBeAfter[ii]+"']").toArray().length>0 ) {
						$this.next().after($this);
						ok=false;
					}
				}
			} while(!ok)
		}
	});
};

Xonomy.harvest=function() { //harvests the contents of an editor
	//Returns xml-as-string.
	var rootElement=$(".xonomy .element").first().toArray()[0];
	var js=Xonomy.harvestElement(rootElement);
	for(var key in Xonomy.namespaces) {
		js.attributes.push({
			type: "attribute",
			name: key,
			value: Xonomy.namespaces[key],
			parent: js
		});
	}
	return Xonomy.js2xml(js);
}
Xonomy.harvestElement=function(htmlElement, jsParent) {
	var js=new Xonomy.surrogate(jsParent);
	js.type="element";
	js.name=htmlElement.getAttribute("data-name");
	js.htmlID=htmlElement.id;
	js.attributes=[];
	var htmlAttributes=$(htmlElement).find(".tag.opening > .attributes").toArray()[0];
	for(var i=0; i<htmlAttributes.childNodes.length; i++) {
		var htmlAttribute=htmlAttributes.childNodes[i];
		if($(htmlAttribute).hasClass("attribute")) js["attributes"].push(Xonomy.harvestAttribute(htmlAttribute, js));
	}
	js.children=[];
	var htmlChildren=$(htmlElement).children(".children").toArray()[0];
	for(var i=0; i<htmlChildren.childNodes.length; i++) {
		var htmlChild=htmlChildren.childNodes[i];
		if($(htmlChild).hasClass("element")) js["children"].push(Xonomy.harvestElement(htmlChild, js));
		else if($(htmlChild).hasClass("textnode")) js["children"].push(Xonomy.harvestText(htmlChild, js));
	}
	js=Xonomy.enrichElement(js);
	return js;
};
Xonomy.harvestAttribute=function(htmlAttribute, jsParent) {
	var js = new Xonomy.surrogate(jsParent);
	js.type = "attribute";
	js.name = htmlAttribute.getAttribute("data-name");
	js.htmlID = htmlAttribute.id;
	js.value = htmlAttribute.getAttribute("data-value");
	return js;
}

Xonomy.surrogate=function(jsParent) {
	this.internalParent=jsParent;
}

Xonomy.surrogate.prototype.parent=function() {
	if (!this.internalParent) {
		this.internalParent=Xonomy.harvestParentOf(this);
	}
	return this.internalParent;
}

Xonomy.harvestText = function (htmlText, jsParent) {
	var js = new Xonomy.surrogate(jsParent);
	js.type = "text";
	js.htmlID = htmlText.id;
	js.value = htmlText.getAttribute("data-value");
	return js;
}

Xonomy.harvestParentOf=function(js) {
	var jsParent=null;
	var $parent=$("#"+js.htmlID).parent().closest(".element");
	if($parent.toArray().length==1) {
		jsParent=Xonomy.harvestElement($parent.toArray()[0]);
		for(var i=0; i<jsParent.attributes.length; i++) if(jsParent.attributes[i].htmlID==js.htmlID) jsParent.attributes[i]=js;
		for(var i=0; i<jsParent.children.length; i++) if(jsParent.children[i].htmlID==js.htmlID) jsParent.children[i]=js;
	}
	return jsParent;
};

Xonomy.render=function(data, editor, docSpec) { //renders the contents of an editor
	//The data can be a Xonomy-compliant XML document, a Xonomy-compliant xml-as-string,
	//or a Xonomy-compliant JavaScript object.
	//The editor can be an HTML element, or the string ID of one.
	Xonomy.docSpec=docSpec;
	Xonomy.verifyDocSpec();
	
	//Clear namespace cache:
	Xonomy.namespaces={};
	
	//Convert doc to a JavaScript object, if it isn't a JavaScript object already:
	if(typeof(data)=="string") data=$.parseXML(data);
	if(data.documentElement) data=Xonomy.xml2js(data);
	
	//Make sure editor refers to an HTML element, if it doesn't already:
	if(typeof(editor)=="string") editor=document.getElementById(editor);
	if(!$(editor).hasClass("xonomy")) $(editor).addClass("xonomy"); //make sure it has class "xonomy"
	
	$(editor).hide();
	editor.innerHTML=Xonomy.renderElement(data, editor);
	$(editor).show();
	
	//Make sure the "click off" handler is attached:
	$(document.body).off("click", Xonomy.clickoff);
	$(document.body).on("click", Xonomy.clickoff);

	//Make sure the "drag end" handler is attached:
	$(document.body).off("dragend", Xonomy.dragend);
	$(document.body).on("dragend", Xonomy.dragend);
	
	Xonomy.refresh();
	Xonomy.validate();
};
Xonomy.renderElement=function(element) {
	var htmlID=Xonomy.nextID();
	Xonomy.verifyDocSpecElement(element.name);
	var spec=Xonomy.docSpec.elements[element.name];
	var classNames="element";
	if(spec.canDropTo && spec.canDropTo.length>0) classNames+=" draggable";
	var hasText = spec.hasText(element);
	if(hasText) classNames+=" hasText";
	if(spec.inlineMenu && spec.inlineMenu.length>0) classNames+=" hasInlineMenu";
	if(spec.oneliner(element)) classNames+=" oneliner";
	if(spec.collapsed(element)) classNames+=" collapsed";
	if(spec.menu.length>0) classNames+=" hasMenu"; //not always accurate: whether an element has a menu is actually determined at runtime
	var html="";
	html+='<div data-name="'+element.name+'" id="'+htmlID+'" class="'+classNames+'">';
		html+='<span class="connector">';
			html+='<span class="plusminus" onclick="Xonomy.plusminus(\''+htmlID+'\')"></span>';
			html+='<span class="draghandle" draggable="true" ondragstart="Xonomy.drag(event)"></span>';
		html+='</span>';
		html+='<span class="tag opening">';
			html+='<span class="punc">&lt;</span>';
			html+='<span class="name" onclick="Xonomy.click(\''+htmlID+'\', \'openingTagName\')">'+element.name+'</span>';
			html+='<span class="warner"><span class="inside" onclick="Xonomy.click(\''+htmlID+'\', \'warner\')"></span></span>';
			html+='<span class="attributes">';
				for(var i=0; i<element.attributes.length; i++) {
					Xonomy.verifyDocSpecAttribute(element.name, element.attributes[i].name);
					html+=Xonomy.renderAttribute(element.attributes[i]);
				}
			html+='</span>';
			html+='<span class="punc slash">/</span>';
			html+='<span class="punc">&gt;</span>';
		html+='</span>';
		html+='<span class="childrenCollapsed" onclick="Xonomy.plusminus(\''+htmlID+'\', true)">&middot;&middot;&middot;</span>';
		html+='<div class="children">';
			var prevChildType="";
			if(hasText && (element.children.length==0 || element.children[0].type=="element")) {
				html+=Xonomy.renderText({type: "text", value: ""}); //if inline layout, insert empty text node between two elements
			}
			for(var i=0; i<element.children.length; i++) {
				var child=element.children[i];
				if(hasText && prevChildType=="element" && child.type=="element") {
					html+=Xonomy.renderText({type: "text", value: ""}); //if inline layout, insert empty text node between two elements
				}
				if(child.type=="text") html+=Xonomy.renderText(child); //text node
				else if(child.type=="element") html+=Xonomy.renderElement(child); //element node
				prevChildType=child.type;
			}
			if(hasText && element.children.length>1 && element.children[element.children.length-1].type=="element") {
				html+=Xonomy.renderText({type: "text", value: ""}); //if inline layout, insert empty text node between two elements
			}
		html+='</div>';
		html+='<span class="tag closing">';
			html+='<span class="punc">&lt;</span>';
			html+='<span class="punc">/</span>';
			html+='<span class="name" onclick="Xonomy.click(\''+htmlID+'\', \'closingTagName\')">'+element.name+'</span>';
			html+='<span class="punc">&gt;</span>';
		html+='</span>';
	html+='</div>';
	element.htmlID = htmlID;
	return html;
};
Xonomy.renderAttribute=function(attribute) {
	var htmlID=Xonomy.nextID();
	var readonly=false; //TBE
	classNames="attribute"; if(readonly) classNames+=" readonly";
	var html="";
	html+='<span data-name="'+attribute.name+'" data-value="'+Xonomy.xmlEscape(attribute.value)+'" id="'+htmlID+'" class="'+classNames+'">';
		html+='<span class="punc"> </span>';
		var onclick=''; if(!readonly) onclick=' onclick="Xonomy.click(\''+htmlID+'\', \'attributeName\')"';
		html+='<span class="name"'+onclick+'>'+attribute.name+'</span>';
		html+='<span class="warner"><span class="inside" onclick="Xonomy.click(\''+htmlID+'\', \'warner\')"></span></span>';
		html+='<span class="punc">=</span>';
		var onclick=''; if(!readonly) onclick=' onclick="Xonomy.click(\''+htmlID+'\', \'attributeValue\')"';
		html+='<span class="valueContainer"'+onclick+'>';
			html+='<span class="punc">"</span>';
			html+='<span class="value">'+Xonomy.xmlEscape(attribute.value)+'</span>';
			html+='<span class="punc">"</span>';
		html+='</span>';
	html+='</span>';
	attribute.htmlID = htmlID;
	return html;
};
Xonomy.renderText=function(text) {
	var htmlID=Xonomy.nextID();
	var classNames="textnode";
	if($.trim(text.value)=="") classNames+=" whitespace";
	if(text.value=="") classNames+=" empty";
	var html="";
	html+='<div id="'+htmlID+'" data-value="'+Xonomy.xmlEscape(text.value)+'" class="'+classNames+'">';
		html+='<span class="connector"></span>';
		html+='<span class="value" onclick="Xonomy.click(\''+htmlID+'\', \'text\')"><span class="insertionPoint"><span class="inside"></span></span><span class="dots"></span>'+Xonomy.chewText(text.value)+'</span>';
	html+='</div>';
	text.htmlID = htmlID;
	return html;
}

Xonomy.chewText=function(txt) {
	var ret="";
	ret+="<span class='word'>"; //start word
	for(var i=0; i<txt.length; i++) {
		if(txt[i]==" ") ret+="</span>"; //end word
		var t=Xonomy.xmlEscape(txt[i])
		if(i==0 && t==" ") t="&nbsp;"; //leading space
		if(i==txt.length-1 && t==" ") t="&nbsp;"; //trailing space
		ret+="<span class='char'>"+t+"<span class='selector'><span class='inside' onclick='Xonomy.charClick(this.parentNode.parentNode)'></span></span></span>";
		if(txt[i]==" ") ret+="<span class='word'>"; //start word
	}
	ret+="</span>"; //end word
	return ret;
};
Xonomy.charClick=function(c) {
	Xonomy.clickoff();
	Xonomy.notclick=true;
	if(
		$(".xonomy .char.on").toArray().length==1 && //if there is precisely one previously selected character
		$(".xonomy .char.on").closest(".element").is($(c).closest(".element")) //and if it has the same parent element as this character
	) {
		var $element=$(".xonomy .char.on").closest(".element");
		var chars=$element.find(".char").toArray();
		var iFrom=$.inArray($(".xonomy .char.on").toArray()[0], chars);
		var iTill=$.inArray(c, chars);
		if(iFrom>iTill) {var temp=iFrom; iFrom=iTill; iTill=temp;}
		for(var i=0; i<chars.length; i++) { //highlight all chars between start and end
			if(i>=iFrom && i<=iTill) $(chars[i]).addClass("on");
		}
		//Save for later the info Xonomy needs to know what to wrap:
		Xonomy.textFromID=$(chars[iFrom]).closest(".textnode").attr("id");
		Xonomy.textTillID=$(chars[iTill]).closest(".textnode").attr("id");
		Xonomy.textFromIndex=$.inArray(chars[iFrom], $("#"+Xonomy.textFromID).find(".char").toArray());
		Xonomy.textTillIndex=$.inArray(chars[iTill], $("#"+Xonomy.textTillID).find(".char").toArray());
		//Show inline menu etc:
		var htmlID=$element.attr("id");
		var content=Xonomy.inlineMenu(htmlID); //compose bubble content
		if(content!="") {
			document.body.appendChild(Xonomy.makeBubble(content)); //create bubble
			Xonomy.showBubble($("#"+htmlID+" .char.on").last()); //anchor bubble to highlighted chars
		}
		Xonomy.clearChars=true;
	} else {
		$(".xonomy .char.on").removeClass("on");
		$(c).addClass("on");
	}
};
Xonomy.wrap=function(htmlID, param) {
	Xonomy.clickoff();
	var xml=param.template;
	var ph=param.placeholder;
	if(Xonomy.textFromID==Xonomy.textTillID) { //abc --> a<XYZ>b</XYZ>c
		var jsOld=Xonomy.harvestText(document.getElementById(Xonomy.textFromID));
		var txtOpen=jsOld.value.substring(0, Xonomy.textFromIndex);
		var txtMiddle=jsOld.value.substring(Xonomy.textFromIndex, Xonomy.textTillIndex+1);
		var txtClose=jsOld.value.substring(Xonomy.textTillIndex+1);
		xml=xml.replace(ph, Xonomy.xmlEscape(txtMiddle));
		var html="";
		html+=Xonomy.renderText({type: "text", value: txtOpen});
		html+=Xonomy.renderElement(Xonomy.xml2js(xml));
		html+=Xonomy.renderText({type: "text", value: txtClose});
		$("#"+Xonomy.textFromID).replaceWith(html);
	} else { //ab<...>cd --> a<XYZ>b<...>c</XYZ>d
		var jsOldOpen=Xonomy.harvestText(document.getElementById(Xonomy.textFromID));
		var jsOldClose=Xonomy.harvestText(document.getElementById(Xonomy.textTillID));
		var txtOpen=jsOldOpen.value.substring(0, Xonomy.textFromIndex);
		var txtMiddleOpen=jsOldOpen.value.substring(Xonomy.textFromIndex);
		var txtMiddleClose=jsOldClose.value.substring(0, Xonomy.textTillIndex+1);
		var txtClose=jsOldClose.value.substring(Xonomy.textTillIndex+1);
		xml=xml.replace(ph, Xonomy.xmlEscape(txtMiddleOpen)+ph);
		$("#"+Xonomy.textFromID).nextUntil("#"+Xonomy.textTillID).each(function(){
			if($(this).hasClass("element")) xml=xml.replace(ph, Xonomy.js2xml(Xonomy.harvestElement(this))+ph);
			else if($(this).hasClass("textnode")) xml=xml.replace(ph, Xonomy.js2xml(Xonomy.harvestText(this))+ph);
		});
		xml=xml.replace(ph, Xonomy.xmlEscape(txtMiddleClose));
		$("#"+Xonomy.textFromID).nextUntil("#"+Xonomy.textTillID).remove();
		$("#"+Xonomy.textTillID).remove();
		var html="";
		html+=Xonomy.renderText({type: "text", value: txtOpen});
		html+=Xonomy.renderElement(Xonomy.xml2js(xml));
		html+=Xonomy.renderText({type: "text", value: txtClose});
		$("#"+Xonomy.textFromID).replaceWith(html);
	}
	Xonomy.refresh();
};
Xonomy.unwrap=function(htmlID, param) {
	Xonomy.clickoff();
	$("#"+htmlID).replaceWith($("#"+htmlID+" > .children > *"));
	Xonomy.refresh();
};

Xonomy.plusminus=function(htmlID, forceExpand) {
	var $element=$("#"+htmlID);
	var $children=$element.children(".children");
	if($element.hasClass("collapsed")) {
		$children.hide();
		$element.removeClass("collapsed");
		if($element.hasClass("oneliner")) $children.fadeIn("fast"); else $children.slideDown("fast");
	} else if(!forceExpand) {
		Xonomy.updateCollapsoid(htmlID);
		if($element.hasClass("oneliner")) $children.fadeOut("fast", function(){ $element.addClass("collapsed"); });
		else $children.slideUp("fast", function(){ $element.addClass("collapsed"); });
	}
};
Xonomy.updateCollapsoid=function(htmlID) {
	var $element=$("#"+htmlID);
	var whisper="";
	var abbreviated=false;
	$element.find(".textnode").each(function(){
		var txt=Xonomy.harvestText(this).value;
		if($element.hasClass("oneliner")) {
			whisper+=txt;
		} else {
			for(var i=0; i<txt.length; i++) {
				if(whisper.length<25) whisper+=txt[i]; else abbreviated=true;
			}
		}
	});
	if(abbreviated && !$element.hasClass("oneliner") && whisper!="...") whisper+="...";
	if(whisper=="") whisper="...";
	$element.children(".childrenCollapsed").html(whisper);
};

Xonomy.click=function(htmlID, what) {
	if(!Xonomy.notclick) {
		Xonomy.clickoff();
		$(".xonomy .char.on").removeClass("on");
		if(what=="openingTagName" || what=="closingTagName") {
			$("#"+htmlID).addClass("current"); //make the element current
			var content=Xonomy.elementMenu(htmlID); //compose bubble content
			if(content!="") {
				document.body.appendChild(Xonomy.makeBubble(content)); //create bubble
				if(what=="openingTagName") Xonomy.showBubble($("#"+htmlID+" > .tag.opening > .name")); //anchor bubble to opening tag
				if(what=="closingTagName") Xonomy.showBubble($("#"+htmlID+" > .tag.closing > .name")); //anchor bubble to closing tag
			}
		}
		if(what=="attributeName") {
			$("#"+htmlID).addClass("current"); //make the attribute current
			var content=Xonomy.attributeMenu(htmlID); //compose bubble content
			if(content!="") {
				document.body.appendChild(Xonomy.makeBubble(content)); //create bubble
				Xonomy.showBubble($("#"+htmlID+" > .name")); //anchor bubble to attribute name
			}
		}
		if(what=="attributeValue") {
			$("#"+htmlID+" > .valueContainer").addClass("current"); //make attribute value current
			var name=$("#"+htmlID).attr("data-name"); //obtain attribute's name
			var value=$("#"+htmlID).attr("data-value"); //obtain current value
			var elName=$("#"+htmlID).closest(".element").attr("data-name");
			Xonomy.verifyDocSpecAttribute(elName, name);
			var spec=Xonomy.docSpec.elements[elName].attributes[name];
			var content=spec.asker(value, spec.askerParameter); //compose bubble content
			if(content!="") {
				document.body.appendChild(Xonomy.makeBubble(content)); //create bubble
				Xonomy.showBubble($("#"+htmlID+" > .valueContainer > .value")); //anchor bubble to value
				Xonomy.answer=function(val) {
					var obj=document.getElementById(htmlID);
					var html=Xonomy.renderAttribute({type: "attribute", name: name, value: val});
					$(obj).replaceWith(html);
					Xonomy.clickoff();
					Xonomy.changed();
				};
			}
		}
		if(what=="text") {
			$("#"+htmlID).addClass("current");
			var value=$("#"+htmlID).attr("data-value"); //obtain current value
			var elName=$("#"+htmlID).closest(".element").attr("data-name");
			var spec=Xonomy.docSpec.elements[elName];
			if (typeof(spec.asker) != "function") {
				var content=Xonomy.askLongString(value); //compose bubble content  
			} else {
				var content=spec.asker(value, spec.askerParameter); //use specified asker
			}			
			document.body.appendChild(Xonomy.makeBubble(content)); //create bubble
			Xonomy.showBubble($("#"+htmlID+" > .value")); //anchor bubble to value
			Xonomy.answer=function(val) {
				var obj=document.getElementById(htmlID);
				var jsText = {type: "text", value: val};
				var html=Xonomy.renderText(jsText);
				$(obj).replaceWith(html);
				Xonomy.clickoff();
				Xonomy.changed(Xonomy.harvestText(document.getElementById(jsText.htmlID)));
			};
		}
		if(what=="warner") {
			//$("#"+htmlID).addClass("current");
			var content=""; //compose bubble content
			for(var iWarning=0; iWarning<Xonomy.warnings.length; iWarning++) {
				var warning=Xonomy.warnings[iWarning];
				if(warning.htmlID==htmlID) {
					content+="<div class='warning'>"+Xonomy.formatCaption(Xonomy.textByLang(warning.text))+"</div>";
				}
			}
			document.body.appendChild(Xonomy.makeBubble(content)); //create bubble
			Xonomy.showBubble($("#"+htmlID+" .warner .inside").first()); //anchor bubble to warner
		}
		Xonomy.notclick=true;
	}
};
Xonomy.notclick=false; //should the latest click-off event be ignored?
Xonomy.clearChars=false; //if true, un-highlight any highlighted characters at the next click-off event
Xonomy.clickoff=function() { //event handler for the document-wide click-off event.
	if(!Xonomy.notclick) {
		Xonomy.destroyBubble();
		$(".xonomy .current").removeClass("current");
		if(Xonomy.clearChars) {
			$(".xonomy .char.on").removeClass("on");
			Xonomy.clearChars=false;
		}
	}
	Xonomy.notclick=false;
};

Xonomy.destroyBubble=function() {
	if(document.getElementById("xonomyBubble")) {
		var bubble=document.getElementById("xonomyBubble");
		bubble.parentNode.removeChild(bubble);
	}
};
Xonomy.makeBubble=function(content) {
	Xonomy.destroyBubble();
	var bubble=document.createElement("div");
	bubble.id="xonomyBubble";
	bubble.innerHTML="<div class='inside' onclick='Xonomy.notclick=true;'>"
			+"<div id='xonomyBubbleContent'>"+content+"</div>"
		+"</div>";
	return bubble;
};
Xonomy.showBubble=function($anchor) {
	var $bubble=$("#xonomyBubble");
	var offset=$anchor.offset(); var left=offset.left; var top=offset.top;
	var screenWidth=$("body").width();
	if(left<screenWidth/2) {
		var width=$anchor.width(); if(width>40) width=40;
		var height=$anchor.height(); if(height>25) height=25;
		$bubble.css({top: (top+height)+"px", left: (left+width-15)+"px"});
	} else {
		var width=$anchor.width(); if(width>40) width=40;
		var height=$anchor.height(); if(height>25) height=25;
		$bubble.addClass("rightAnchored");
		$bubble.css({top: (top+height)+"px", right: (screenWidth-left)+"px"});
	}
	$bubble.slideDown("fast", function() {
		$bubble.find(".focusme").first().focus(); //if the context menu contains anything with the class name 'focusme', focus it.
	});
};

Xonomy.askString=function(defaultString) {
	var html="";
	html+="<form onsubmit='Xonomy.answer(this.val.value); return false'>";
		html+="<input name='val' class='textbox focusme' value='"+Xonomy.xmlEscape(defaultString)+"'/>";
		html+=" <input type='submit' value='OK'>";
	html+="</form>";
	return html;
};
Xonomy.askLongString=function(defaultString) {
	var html="";
	html+="<form onsubmit='Xonomy.answer(this.val.value); return false'>";
		html+="<textarea name='val' class='textbox focusme' spellcheck='false'>"+Xonomy.xmlEscape(defaultString)+"</textarea>";
		html+="<div class='submitline'><input type='submit' value='OK'></div>";
	html+="</form>";
	return html;
};
Xonomy.askPicklist=function(defaultString, picklist) {
	var html="";
	html+="<div class='menu'>";
	for(var i=0; i<picklist.length; i++) {
		var item=picklist[i];
		if(typeof(item)=="string") item={value: item, caption: ""};
		html+="<div class='menuItem techno"+(item.value==defaultString?" current":"")+"' onclick='Xonomy.answer(\""+Xonomy.xmlEscape(item.value)+"\")'>";
		html+="<span class='punc'>\"</span>";
		html+=Xonomy.xmlEscape(item.value);
		html+="<span class='punc'>\"</span>";
		if(item.caption!="") html+=" <span class='explainer'>"+Xonomy.xmlEscape(Xonomy.textByLang(item.caption))+"</span>";
		html+="</div>";
	}
	html+="</div>";
	return html;
};

Xonomy.attributeMenu=function(htmlID) {
	var name=$("#"+htmlID).attr("data-name"); //obtain attribute's name
	var elName=$("#"+htmlID).closest(".element").attr("data-name"); //obtain element's name
	Xonomy.verifyDocSpecAttribute(elName, name);
	var spec=Xonomy.docSpec.elements[elName].attributes[name];
	var html="";
	for(var i=0; i<spec.menu.length; i++) {
		var item=spec.menu[i];
		var includeIt=!item.hideIf(Xonomy.harvestAttribute(document.getElementById(htmlID)));
		if(includeIt) {
			html+="<div class='menuItem' onclick='Xonomy.callMenuFunction(Xonomy.docSpec.elements[\""+elName+"\"].attributes[\""+name+"\"].menu["+i+"], \""+htmlID+"\")'>";
			html+=Xonomy.formatCaption(Xonomy.textByLang(item.caption));
			html+="</div>";
		}
	}
	if(html!="") html="<div class='menu'>"+html+"</div>";
	return html;
};
Xonomy.elementMenu=function(htmlID) {
	var elName=$("#"+htmlID).attr("data-name"); //obtain element's name
	var spec=Xonomy.docSpec.elements[elName];
	var html="";
	for(var i=0; i<spec.menu.length; i++) {
		var item=spec.menu[i];
		var includeIt=!item.hideIf(Xonomy.harvestElement(document.getElementById(htmlID)));
		if(includeIt) {
			html+="<div class='menuItem' onclick='Xonomy.callMenuFunction(Xonomy.docSpec.elements[\""+elName+"\"].menu["+i+"], \""+htmlID+"\")'>";
			html+=Xonomy.formatCaption(Xonomy.textByLang(item.caption));
			html+="</div>";
		}
	}
	if(html!="") html="<div class='menu'>"+html+"</div>";
	return html;
};
Xonomy.inlineMenu=function(htmlID) {
	var elName=$("#"+htmlID).attr("data-name"); //obtain element's name
	var spec=Xonomy.docSpec.elements[elName];
	var html="";
	for(var i=0; i<spec.inlineMenu.length; i++) {
		var item=spec.inlineMenu[i];
		var includeIt=!item.hideIf(Xonomy.harvestElement(document.getElementById(htmlID)));
		if(includeIt) {
			html+="<div class='menuItem' onclick='Xonomy.callMenuFunction(Xonomy.docSpec.elements[\""+elName+"\"].inlineMenu["+i+"], \""+htmlID+"\")'>";
			html+=Xonomy.formatCaption(Xonomy.textByLang(item.caption));
			html+="</div>";
		}
	}
	if(html!="") html="<div class='menu'>"+html+"</div>";
	return html;
};
Xonomy.callMenuFunction=function(menuItem, htmlID) {
	menuItem.action(htmlID, menuItem.actionParameter);
	Xonomy.changed();
};
Xonomy.formatCaption=function(caption) {
	caption=caption.replace(/\<([^\>]+)\>/g, "<span class='techno'><span class='punc'>&lt;</span><span class='elName'>$1</span><span class='punc'>&gt;</span></span>");
	caption=caption.replace(/\@"([^\"]+)"/g, "<span class='techno'><span class='punc'>\"</span><span class='atValue'>$1</span><span class='punc'>\"</span></span>");
	caption=caption.replace(/\@([^ =]+)="([^\"]+)"/g, "<span class='techno'><span class='atName'>$1</span><span class='punc'>=\"</span><span class='atValue'>$2</span><span class='punc'>\"</span></span>");
	caption=caption.replace(/\@([^ =]+)/g, "<span class='techno'><span class='atName'>$1</span></span>");
	return caption;
};

Xonomy.deleteAttribute=function(htmlID, parameter) {
	Xonomy.clickoff();
	var obj=document.getElementById(htmlID);
	obj.parentNode.removeChild(obj);
	Xonomy.refresh();
};
Xonomy.deleteElement=function(htmlID, parameter) {
	Xonomy.clickoff();
	var obj=document.getElementById(htmlID);
	$(obj).slideUp(function(){
		obj.parentNode.removeChild(obj);
		Xonomy.refresh();
	});
};
Xonomy.newAttribute=function(htmlID, parameter) {
	Xonomy.clickoff();
	var html=Xonomy.renderAttribute({type: "attribute", name: parameter.name, value: parameter.value});
	$("#"+htmlID+" > .tag.opening > .attributes").append(html);
	Xonomy.refresh();
};
Xonomy.newElementChild=function(htmlID, parameter) {
	Xonomy.clickoff();
	var html=Xonomy.renderElement(Xonomy.xml2js(parameter));
	var $html=$(html).hide();
	$("#"+htmlID+" > .children").append($html);
	Xonomy.plusminus(htmlID, true);
	Xonomy.refresh();
	$html.slideDown();
};
Xonomy.newElementBefore=function(htmlID, parameter) {
	Xonomy.clickoff();
	var html=Xonomy.renderElement(Xonomy.xml2js(parameter));
	var $html=$(html).hide();
	$("#"+htmlID).before($html);
	Xonomy.refresh();
	$html.slideDown();
};
Xonomy.newElementAfter=function(htmlID, parameter) {
	Xonomy.clickoff();
	var html=Xonomy.renderElement(Xonomy.xml2js(parameter));
	var $html=$(html).hide();
	$("#"+htmlID).after($html);
	Xonomy.refresh();
	$html.slideDown();
};
Xonomy.replace=function(htmlID, jsNode) {
	Xonomy.clickoff();
	var html="";
	if(jsNode.type=="element") html=Xonomy.renderElement(jsNode);
	if(jsNode.type=="attribute") html=Xonomy.renderAttribute(jsNode);
	if(jsNode.type=="text") html=Xonomy.renderText(jsNode);
	$("#"+htmlID).replaceWith(html);
	Xonomy.refresh();
};

Xonomy.draggingID=null; //what are we dragging?
Xonomy.drag=function(ev) { //called when dragging starts
	Xonomy.clickoff();
	var htmlID=ev.target.parentNode.parentNode.id;
	var $element=$("#"+htmlID);
	var elementName=$element.attr("data-name");
	var elSpec=Xonomy.docSpec.elements[elementName];
	$element.addClass("dragging");
	$(".xonomy .children").append("<div class='elementDropper' ondragover='Xonomy.dragOver(event)' ondragleave='Xonomy.dragOut(event)' ondrop='Xonomy.drop(event)'><div class='inside'></div></div>")
	$(".xonomy .children .element").before("<div class='elementDropper' ondragover='Xonomy.dragOver(event)' ondragleave='Xonomy.dragOut(event)' ondrop='Xonomy.drop(event)'><div class='inside'></div></div>")
	$(".xonomy .children .text").before("<div class='elementDropper' ondragover='Xonomy.dragOver(event)' ondragleave='Xonomy.dragOut(event)' ondrop='Xonomy.drop(event)'><div class='inside'></div></div>")
	$(".xonomy .dragging .elementDropper").remove(); //remove drop targets inside the element being dragged
	$(".xonomy .dragging").prev(".elementDropper").remove(); //remove drop targets from immediately before the element being dragged
	$(".xonomy .dragging").next(".elementDropper").remove(); //remove drop targets from immediately after the element being dragged
	if(elSpec.canDropTo) { //remove the drop target from elements it cannot be dropped into
		var droppers=$(".xonomy .elementDropper").toArray();
		for(var i=0; i<droppers.length; i++) {
			var dropper=droppers[i];
			var parentElementName=$(dropper.parentNode.parentNode).toArray()[0].getAttribute("data-name");
			if($.inArray(parentElementName, elSpec.canDropTo)<0) {
				dropper.parentNode.removeChild(dropper);
			}
		}
	}
	if(elSpec.mustBeBefore) { //remove the drop target from after elements it cannot be after
		var droppers=$(".xonomy .elementDropper").toArray();
		for(var i=0; i<droppers.length; i++) {
			var dropper=droppers[i];
			for(var ii=0; ii<elSpec.mustBeBefore.length; ii++) {
				if( $(dropper).prevAll("*[data-name='"+elSpec.mustBeBefore[ii]+"']").toArray().length>0 ) {
					dropper.parentNode.removeChild(dropper);
				}
			}
		}
	}
	if(elSpec.mustBeAfter) { //remove the drop target from before elements it cannot be before
		var droppers=$(".xonomy .elementDropper").toArray();
		for(var i=0; i<droppers.length; i++) {
			var dropper=droppers[i];
			for(var ii=0; ii<elSpec.mustBeAfter.length; ii++) {
				if( $(dropper).nextAll("*[data-name='"+elSpec.mustBeAfter[ii]+"']").toArray().length>0 ) {
					dropper.parentNode.removeChild(dropper);
				}
			}
		}
	}
	Xonomy.draggingID=htmlID;
	ev.dataTransfer.setData("text", htmlID);
	Xonomy.refresh();
};
Xonomy.dragOver=function(ev) {
	ev.preventDefault();
	$(ev.target.parentNode).addClass("activeDropper");
};
Xonomy.dragOut=function(ev) {
	ev.preventDefault();
	$(".xonomy .activeDropper").removeClass("activeDropper");
};
Xonomy.drop=function(ev) {
	ev.preventDefault();
	var node=document.getElementById(Xonomy.draggingID); //the thing we are moving
	$(ev.target.parentNode).replaceWith(node);
	Xonomy.changed();
};
Xonomy.dragend=function(ev) {
	$(".xonomy .attributeDropper").remove();
	$(".xonomy .elementDropper").remove();
	$(".xonomy .dragging").removeClass("dragging");
	Xonomy.refresh();
};

Xonomy.changed=function(jsElement) { //called when the document changes
	Xonomy.validate();
	Xonomy.docSpec.onchange(jsElement); //report that the document has changed
};
Xonomy.validate=function() {
	var js=Xonomy.harvestElement($(".xonomy .element").toArray()[0], null);
	$(".xonomy .invalid").removeClass("invalid");
	Xonomy.warnings=[];
	Xonomy.docSpec.validate(js); //validate the document
	for(var iWarning=0; iWarning<Xonomy.warnings.length; iWarning++) {
		var warning=Xonomy.warnings[iWarning];
		$("#"+warning.htmlID).addClass("invalid");
	}
};
Xonomy.warnings=[]; //array of {htmlID: "", text: ""}

Xonomy.textByLang=function(str) {
	//str = eg. "en: Delete | de: Löschen | fr: Supprimer"
	var ret=str;
	var segs=str.split("|");
	for(var i=0; i<segs.length; i++) {
		var seg=$.trim(segs[i]);
		if(seg.indexOf(Xonomy.lang+":")==0) {
			ret=seg.substring((Xonomy.lang+":").length, ret.length);
		}
	}
	ret=$.trim(ret);
	return ret;
};