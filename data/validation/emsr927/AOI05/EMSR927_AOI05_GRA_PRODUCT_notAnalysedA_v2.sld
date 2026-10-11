<?xml version='1.0' encoding='UTF-8'?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:se="http://www.opengis.net/se" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.1.0/StyledLayerDescriptor.xsd" version="1.1.0">
  <NamedLayer>
    <se:Name>EMSR927_AOI05_GRA_PRODUCT_notAnalysedA_v2</se:Name>
    <UserStyle>
      <se:Name>EMSR927_AOI05_GRA_PRODUCT_notAnalysedA_v2</se:Name>
      <se:FeatureTypeStyle>
        <se:Rule>
          <se:Abstract>REF_BLP_FEP_DEL_GRA_GRM</se:Abstract>
          <se:Name>Not Analysed</se:Name>
          <se:Description>
            <se:Title>Not Analysed</se:Title>
          </se:Description>
          <ogc:Filter>
            <ogc:Or>
			<ogc:PropertyIsEqualTo>
              <ogc:PropertyName>obj_type</ogc:PropertyName>
              <ogc:Literal>Not Analysed</ogc:Literal>
            </ogc:PropertyIsEqualTo>
			<ogc:PropertyIsEqualTo>
              <ogc:PropertyName>obj_type</ogc:PropertyName>
              <ogc:Literal>Not Analysed - No data</ogc:Literal>
            </ogc:PropertyIsEqualTo>			
		  </ogc:Or>
          </ogc:Filter>
          <se:PolygonSymbolizer>
            <se:Fill>
              <se:GraphicFill>
                <se:Graphic>
                  <se:ExternalGraphic>
                  <se:OnlineResource xlink:href="https://emergency.copernicus.eu/images/svg/sensor_metadata_polygon_fill_not_analysed.svg" xlink:type="simple" />
                  <se:Format>image/svg+xml</se:Format>
               </se:ExternalGraphic>
                  <se:Size>20</se:Size>
                </se:Graphic>
              </se:GraphicFill>
            </se:Fill>
			<VendorOption name="graphic-margin">-1</VendorOption>
            <se:Stroke>
              <se:SvgParameter name="stroke">#000000</se:SvgParameter>
              <se:SvgParameter name="stroke-width">1</se:SvgParameter>
              <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
            </se:Stroke>
          </se:PolygonSymbolizer>
        </se:Rule>
		</se:FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>