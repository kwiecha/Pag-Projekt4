import arcpy

def wczytaj_dane(infc,outfc):
    desc = arcpy.Describe(infc)
    shapefieldname = desc.ShapeFieldName

    rows = arcpy.SearchCursor(infc)

    arcpy.AddField_management(infc, "id_from", "TEXT")
    arcpy.AddField_management(infc, "id_to", "TEXT")
    arcpy.AddField_management(infc, "id_jezdni", "TEXT")
    if not arcpy.ListFields(infc, "max_V"):  
        arcpy.AddField_management(infc, "max_V", "SHORT")

    # Stworzenie nowej klasy punktowej na wezly
    arcpy.CreateFeatureclass_management(outfc[: outfc.rfind("\\")], outfc[outfc.rfind("\\") + 1:], "POINT", "",
                                        "DISABLED", "DISABLED", arcpy.Describe(infc).spatialReference)
    arcpy.AddField_management(outfc, "ident", "TEXT")
    arcpy.AddField_management(outfc, "X", "DOUBLE")
    arcpy.AddField_management(outfc, "Y", "DOUBLE")
    arcpy.AddField_management(outfc, "identJ", "TEXT")

    cursor = arcpy.da.InsertCursor(outfc, ("FID", "SHAPE@XY", "ident", "X", "Y", "identJ"))

    licznik = 0
    for row in rows:
        feat = row.getValue(shapefieldname)

        # Pobranie pierwszego punktu danego obiektu
        startpt = feat.firstPoint

        startx = startpt.X
        starty = startpt.Y

        identStart = ("".join([str(startx)[-4:], str(starty)[-4:]]))

        # Pobranie ostatniego punktu danego obiektu
        endpt = feat.lastPoint

        endx = endpt.X
        endy = endpt.Y

        identEnd = ("".join([str(endx)[-4:], str(endy)[-4:]]))

        identJezdni = "".join([identStart, identEnd])

        cursor.insertRow(("1", (startx, starty), identStart, startx, starty, identJezdni))
        cursor.insertRow(("1", (endx, endy), identEnd, endx, endy, identJezdni))

        # Zaktualizowanie pol id_from, id_to utworzonymi identyfikatorami punktow
        expression = arcpy.AddFieldDelimiters(infc, "FID") + ' = ' + str(licznik)
        with arcpy.da.UpdateCursor(infc, ["id_from", "id_to", "id_jezdni"], expression) as updCur:
            for u in updCur:
                u[0] = identStart
                u[1] = identEnd
                u[2] = identJezdni
                updCur.updateRow(u)

        licznik += 1

    arcpy.DeleteIdentical_management(outfc, "ident")

    # dodanie nowej kolumny, ktora zawierac bedzie max predkosc zalezna od klasy drogi

    with arcpy.da.UpdateCursor(infc, ["klasaDrogi", "max_V"]) as updateCursor:
        for uRow in updateCursor:
            if uRow[0] == 'Z':
                uRow[1] = 50
            elif uRow[0] == 'A':
                uRow[1] = 100
            elif uRow[0] == 'S':
                uRow[1] = 100
            elif uRow[0] == 'GP':
                uRow[1] = 80
            elif uRow[0] == 'G':
                uRow[1] = 60
            elif uRow[0] == 'L':
                uRow[1] = 40
            elif uRow[0] == 'D':
                uRow[1] = 30
            elif uRow[0] == 'I':
                uRow[1] = 50
            updateCursor.updateRow(uRow)
