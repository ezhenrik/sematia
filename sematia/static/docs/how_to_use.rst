.. role:: underline
    :class: underline

How to use
--------

#. **Sign in** using Google account or other operators provided (with Google you need to  allow everything; sign-in does not work if your browser settings block something). The dashboard opens up with a list of all documents imported to Sematia by all users. You can restrict the view to your own texts by clicking “Your contributions”.
#. **Import the document** you have selected to work with from the Papyrological Navigator (http://papyri.info/). Click the button **”New”** at the top right of the page and provide the source URL to the box which opens up. The URL should be of the form, e.g. http://papyri.info/ddbdp/p.adl;;G1/source. You can get the source URL from the Papyrological Navigator either by

    - taking the “Canonical URI” and adding “/source” behind it, **or** 
    - going down to “DDbDP transcription” in the PN page of the document and clicking the [xml] and then copying the URL. You can simply paste the address into the box in Sematia. 
#. **Sematia creates automatically three layers** of the document you imported: original, standard and variation layers (see below what they mean). Moreover, the text is divided into parts according to the handshifts. To expand the view of your imported document (i.e to see the layer options), click anywhere on the box of the imported text, except the title itself (if you click the title, you will see the source xml of the document like in the PN). 
#. When you **select a layer of your document** (click the buttons “original” or “standard”), you see the list of EpiDoc XML elements present in the current text and the color codes show how they are shown in the Transcript. The transcript is the same in both layers and you have the possibility to edit the layer text (e.g. if there are two or more options given in the apparatus of the text in the Papyrological Navigator, you can choose the one you want with the slider and it changes the text in the Plain text view). The Plain text is the form which is taken to the annotation environment. The layers have the following features:

    - :underline:`Original` layer gives you the text as it is preserved in the original papyrus, that is, the abbreviations are not resolved (simply marked with a dummy marker “A”), supplied text is omitted (marked with dummy “SU”), the forms written in the papyrus are included (not the regularized forms). The unclear letters (underdot) are included as “certain” letters, so, if you hesitate with some underdotted letters, you can decide not to annotate those words. It is always advisable to keep the Papyrological Navigator page open as well when working with a text!
    - The :underline:`standard` layer gives the text in the form the editor has interpreted it (i.e. according to the Papyrological Navigator, where later corrections may also be available): the abbreviated words are expanded, the supplied text is included, as are regularized spellings. If the editor has not supplied anything in a *lacuna*, the gap is marked with G. 
    - The :underline:`variation` layer is based on the original layer. This feature is still under development and there is no need to worry about it for the time being.
#. **Export the layer text to the annotation framework.** Click the paper plane icon on the right side of Plain text. This transports the layer text into the Arethusa annotation service in `Perseids Platform <http://sites.tufts.edu/perseids/>`_ (you need to have your own account there).
#. After you have annotated the text, **import your treebank to Sematia**. You first need to “Download Copy” in Arethusa, which saves your treebank to your computer. In Sematia, click ”Upload treebank” in the layer you want to attach the treebank with, browse for the copy you downloaded from Arethusa and select it.
#. If you wish to **discuss** some matters concerning your layers or treebanks, the envelope icon takes you to the discussion mode (everyone who signs in can see the discussion, but only admin and the owner(s) of the document can take part). If the icon is black, there is no discussion, if it is transparent, there is discussion.

.. rubric:: Metadata

The **date** and **provenance** of each document are taken automatically from the PN (HGV) during the import process.

For each **hand** (i.e. “act of writing”) you can add metadata about the handwriting, the writer / author and text type.

In the expanded view of a document, you see either a number 1 with three layers, or several consecutive numbers, if there are several hands in one papyrus. Under the number is a cogwheel icon which opens up a window where metadata can be inserted.

The idea is to add info, if it exists. Otherwise, leave blank.

**Handwriting**
    - You can write a :underline:`description of the hand as it is in the edition`, be it editio princeps or later editions or paleographical handbooks.
    - :underline:`“Custom description”` is your own view of the hand (if you have one, based on the original or an image).
    - The level of :underline:`professionality` can be added from the drop-down menu. If you are sure that the text is written by a scribal professional, choose “Professional”. If the hand is clearly written by someone not accustomed to write, choose “Non-professional”. In private letters, the hand can be practised, but it is uncertain if the writer is a professional, then choose “Practised letterhand”. In all other cases, choose (not known).
    - If you know that the :underline:`same handwriting` is attested in other documents, add the stable URL of that document into the box, e.g. http://papyri.info/ddbdp/p.lond;7;2191 and separate several documents by comma.

**Writer and author**

    - Name and title of the :underline:`actual writer`, if they are known. By actual writer, we mean the person who held the pen and wrote down the text. (Very often this has to be left blank)
    - Name and title of the :underline:`scribal official` in charge of the text, e.g. the notary who has signed the document or has been mentioned in the text.
    - Name and title of the :underline:`author of the text`. By author, we mean the person whom we may expect to be in charge of the text, e.g. the petitioner in a petition, the sender of the private letter, i.e. the person who could have dictated to a scribe what he wants to have written down. Contracts, however, are not normally authored by the contracting parties.

**Text type**
    - Choose from the drop-down menu. The main categories include some subcategories. For example, you can choose only “Letter” or only “Contract”, or be more specific and choose the type of the letter or type of the contract. If the subcategories do not match to your document, use the main ones. If none of the options is suitable, use “Other”.

**Addressee**
    - If there is someone, to whom the document is addressed to, add the applicable information: Professional / non-professional, name and title.