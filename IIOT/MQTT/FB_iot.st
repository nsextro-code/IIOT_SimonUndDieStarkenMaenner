

FUNCTION_BLOCK FB_iot
VAR_INPUT
    iUSS1 : UINT;  // Füllstand rot   (Ultraschallsensor 1)
    iUSS2 : UINT;  // Füllstand blau  (Ultraschallsensor 2)
    iUSS3 : UINT;  // Füllstand grün  (Ultraschallsensor 3)
END_VAR
VAR
    fbMqttClient           : FB_IotMqttClient;
    sMessageToPublish      : STRING(255);
    tmrSendMessageInterval : TON := (PT := T#10S);
    first_cycle            : BOOL := TRUE;
    bStaticPublished       : BOOL := FALSE;
END_VAR



IF first_cycle THEN
    fbMqttClient.sHostName     := '158.180.44.197';
    fbMqttClient.nHostPort     := 1883;
    fbMqttClient.sTopicPrefix  := 'aut/SoSe26/SimonUndDieStarkenMaenner/';
    fbMqttClient.sClientId     := 'SimonUndDieStarkenMaenner-LF';
    fbMqttClient.sUserName     := 'bobm';
    fbMqttClient.sUserPassword := 'letmein';
    first_cycle := FALSE;
END_IF

fbMqttClient.Execute(bConnect := TRUE);

IF fbMqttClient.bConnected THEN

    IF NOT bStaticPublished THEN
        
        sMessageToPublish := 'Simon und die starken Männer';
        fbMqttClient.Publish(sTopic := '$$groupsname', pPayload := ADR(sMessageToPublish), nPayloadSize := LEN(sMessageToPublish) + 1, eQoS := TcIotMqttQos.AtMostOnceDelivery, bRetain := TRUE, bQueue := TRUE);

        
        sMessageToPublish := 'Franz, Jäscke, Sextro';
        fbMqttClient.Publish(sTopic := 'names', pPayload := ADR(sMessageToPublish), nPayloadSize := LEN(sMessageToPublish) + 1, eQoS := TcIotMqttQos.AtMostOnceDelivery, bRetain := TRUE, bQueue := TRUE);

        
        sMessageToPublish := 'g';
        fbMqttClient.Publish(sTopic := 'Fuellstand_rot/$$unit', pPayload := ADR(sMessageToPublish), nPayloadSize := LEN(sMessageToPublish) + 1, eQoS := TcIotMqttQos.AtMostOnceDelivery, bRetain := TRUE, bQueue := TRUE);
        fbMqttClient.Publish(sTopic := 'Fuellstand_blau/$$unit', pPayload := ADR(sMessageToPublish), nPayloadSize := LEN(sMessageToPublish) + 1, eQoS := TcIotMqttQos.AtMostOnceDelivery, bRetain := TRUE, bQueue := TRUE);
        fbMqttClient.Publish(sTopic := 'Fuellstand_gruen/$$unit', pPayload := ADR(sMessageToPublish), nPayloadSize := LEN(sMessageToPublish) + 1, eQoS := TcIotMqttQos.AtMostOnceDelivery, bRetain := TRUE, bQueue := TRUE);

        bStaticPublished := TRUE;
    END_IF

    
    tmrSendMessageInterval(IN := TRUE);
    IF tmrSendMessageInterval.Q THEN
        tmrSendMessageInterval(IN := FALSE);

        sMessageToPublish := UINT_TO_STRING(iUSS1);
        fbMqttClient.Publish(sTopic := 'Fuellstand_rot', pPayload := ADR(sMessageToPublish), nPayloadSize := LEN(sMessageToPublish) + 1, eQoS := TcIotMqttQos.AtMostOnceDelivery, bRetain := TRUE, bQueue := TRUE);

        sMessageToPublish := UINT_TO_STRING(iUSS2);
        fbMqttClient.Publish(sTopic := 'Fuellstand_blau', pPayload := ADR(sMessageToPublish), nPayloadSize := LEN(sMessageToPublish) + 1, eQoS := TcIotMqttQos.AtMostOnceDelivery, bRetain := TRUE, bQueue := TRUE);

        sMessageToPublish := UINT_TO_STRING(iUSS3);
        fbMqttClient.Publish(sTopic := 'Fuellstand_gruen', pPayload := ADR(sMessageToPublish), nPayloadSize := LEN(sMessageToPublish) + 1, eQoS := TcIotMqttQos.AtMostOnceDelivery, bRetain := TRUE, bQueue := TRUE);
    END_IF
END_IF


