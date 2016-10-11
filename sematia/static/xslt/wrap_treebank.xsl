<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    xmlns:oa="http://www.w3.org/ns/oa#"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:prov="http://www.w3.org/ns/prov#"
    xmlns:cnt="http://www.w3.org/2008/content#"
    xmlns:treebank="http://nlp.perseus.tufts.edu/syntax/treebank/1.5"
    version="1.0">
    
    <!-- this template wraps a treebank annotation in an OA container.
         
         parameters 
            e_datetime - the datetime of the serialization
            e_collection - the urn of the CITE collection which the annotation is/will be a member of
            e_docuri - target of the annotation, if supplied will override anything in the template
    -->
    
    <xsl:param name="e_datetime"/>
    <xsl:param name="e_collection"/>
    <xsl:param name="e_docuri"/>
    <xsl:param name="e_agenturi"/>
    <xsl:param name="e_appuri"/>
    <xsl:param name="e_format" select="'aldt'"/>
    <xsl:param name="e_attachtoroot" select="true()"/>
    <xsl:param name="e_dir" select="'ltr'"/>
    
    <!-- override the document_id and subdoc if we were passed a document uri -->
    <xsl:variable name="subdoc_override">
    <xsl:choose>
        <xsl:when test="contains($e_docuri,'urn:cts:')">
            <!-- extract the passage component it's the substring after the 4th ':' -->
            <!-- but note this breaks if individual parts of the urn are namespaced separately from the whole -->
            <xsl:value-of select="substring-after(substring-after(substring-after($e_docuri,'urn:cts:'),':'),':')"/>
        </xsl:when>
        <xsl:otherwise/>
    </xsl:choose>
    </xsl:variable>
    <xsl:variable name="doc_override">
        <xsl:choose>
            <xsl:when test="contains($e_docuri,'urn:cts:')">
                <!-- extract the passage component it's the substring after the 4th ':' -->
                <!-- but note this breaks if individual parts of the urn are namespaced separately from the whole -->
                <xsl:value-of select="substring-before($e_docuri,concat(':',$subdoc_override))"/>
            </xsl:when>
            <xsl:when test="$e_docuri != ''">
                <xsl:value-of select="$e_docuri"/>
            </xsl:when>
            <xsl:otherwise/>
        </xsl:choose>
    </xsl:variable>
    
    <xsl:output indent="yes"></xsl:output>
    <xsl:strip-space elements="*"/>
    
    <xsl:template match="/">
        
       
        <xsl:variable name="target">
            <xsl:choose>
                <xsl:when test="$e_docuri"><xsl:value-of select="$e_docuri"/></xsl:when>
                <xsl:otherwise><xsl:value-of select="//sentence[1]/@document_id"/></xsl:otherwise>
            </xsl:choose>
        </xsl:variable>  
        
        <!-- a hack to get a uuid for the body -->
        <xsl:variable name="bodyid" select="concat('urn:uuid',generate-id(//treebank))"/>
        <xsl:variable name="lang" select="//treebank/@xml:lang"/>
        <xsl:variable name="collection">
            <xsl:choose>
                <xsl:when test="$e_collection"><xsl:value-of select="$e_collection"/></xsl:when>
                <xsl:otherwise><xsl:value-of select="concat('urn:cite:perseus:',$lang,'tb')"/></xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
        <xsl:element name="RDF" namespace="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
            <xsl:element name="Annotation" namespace="http://www.w3.org/ns/oa#">
                <xsl:element name="memberOf" xmlns="http://purl.org/dc/dcam/">
                    <xsl:attribute name="rdf:resource"><xsl:value-of select="$collection"/></xsl:attribute>
                </xsl:element>
                <xsl:element name="hasTarget" namespace="http://www.w3.org/ns/oa#">
                    <xsl:attribute name="rdf:resource"><xsl:value-of select="$target"/></xsl:attribute>
                </xsl:element>
                <xsl:element name="hasBody" namespace="http://www.w3.org/ns/oa#">
                    <xsl:attribute name="rdf:resource"><xsl:value-of select="$bodyid"/></xsl:attribute>
                </xsl:element>
                <!-- TODO this isn't the best motivation  we are going to need to subclass -->
                <xsl:element name="isMotivatedBy" namespace="http://www.w3.org/ns/oa#">
                    <xsl:attribute name="rdf:resource">oa:linking</xsl:attribute>
                </xsl:element>
            <xsl:element name="ContentAsXML" namespace="http://www.w3.org/ns/oa#">
                <xsl:attribute name="rdf:about"><xsl:value-of select="$bodyid"/></xsl:attribute>
                <xsl:element name="cnt:rest">
                    <xsl:attribute name="rdf:parseType">Literal</xsl:attribute>
                    <xsl:apply-templates></xsl:apply-templates>
                </xsl:element>
            </xsl:element>
            </xsl:element>
        </xsl:element>
    </xsl:template>
    
    <xsl:template match="treebank|treebank:treebank">
        <xsl:element name="treebank">
            <xsl:copy-of select="@*[not(name(.) = 'direction') and not(name(.) = 'xmlns') and not(name(.) = 'format')]"/>
            <xsl:attribute name="direction">
                <xsl:choose>
                    <xsl:when test="@dir"><xsl:value-of select="@dir"/></xsl:when>
                    <xsl:otherwise><xsl:value-of select="$e_dir"/></xsl:otherwise>
                </xsl:choose>
            </xsl:attribute>
            <xsl:attribute name="format">
                <xsl:value-of select="$e_format"/>
            </xsl:attribute>
            <xsl:apply-templates select="node()[(local-name(.) = 'date')]"></xsl:apply-templates>
            <xsl:apply-templates select="node()[(local-name(.) = 'comment')]"></xsl:apply-templates>
            <xsl:if test="$e_agenturi">
            <xsl:element name="annotator">
                <xsl:element name="short"/>
                <xsl:element name="name"/>
                <xsl:element name="address"/>
                <xsl:element name="uri"><xsl:value-of select="$e_agenturi"/></xsl:element>
            </xsl:element>
            </xsl:if>
            <xsl:if test="$e_appuri">
                <xsl:element name="annotator">
                    <xsl:element name="short"/>
                    <xsl:element name="name"/>
                    <xsl:element name="address"/>
                    <xsl:element name="uri"><xsl:value-of select="$e_appuri"/></xsl:element>
                </xsl:element>
            </xsl:if>
            <xsl:apply-templates select="node()[not(local-name(.) = 'date') and not(local-name(.) = 'comment')]"></xsl:apply-templates>
        </xsl:element>
    </xsl:template>

    <xsl:template match="@document_id">
        <xsl:choose>
            <xsl:when test="$doc_override != ''">
                <xsl:attribute name="document_id"><xsl:value-of select="$doc_override"/></xsl:attribute>
            </xsl:when>
            <xsl:otherwise><xsl:copy/></xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template match="@subdoc">
        <xsl:choose>
            <xsl:when test="$subdoc_override != ''">
                <xsl:attribute name="subdoc"><xsl:value-of select="$subdoc_override"/></xsl:attribute>
            </xsl:when>
            <xsl:otherwise><xsl:copy/></xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="@head">
        <xsl:attribute name="head">
          <xsl:choose>
            <xsl:when test=". = '0' and (not($e_attachtoroot)  or $e_attachtoroot = '')"></xsl:when>
            <xsl:otherwise><xsl:value-of select="."/></xsl:otherwise>
          </xsl:choose>
        </xsl:attribute>
    </xsl:template>
    
    <xsl:template match="@*">
        <xsl:copy/>
    </xsl:template>

    <xsl:template match="text()">
        <xsl:copy/>
    </xsl:template>
    
    <xsl:template match="*">
        <xsl:element name="{local-name(.)}">
            <xsl:apply-templates select="@*[not(name(.) = 'xmlns')]"/>
            <xsl:apply-templates select="*|text()"/>
        </xsl:element>
        
    </xsl:template>
    
</xsl:stylesheet>
