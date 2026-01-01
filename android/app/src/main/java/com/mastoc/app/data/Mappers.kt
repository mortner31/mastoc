package com.mastoc.app.data

import com.mastoc.app.data.api.dto.ClimbDto
import com.mastoc.app.data.api.dto.FaceDto
import com.mastoc.app.data.api.dto.FaceSetupDto
import com.mastoc.app.data.api.dto.HoldDto
import com.mastoc.app.data.local.ClimbEntity
import com.mastoc.app.data.local.FaceEntity
import com.mastoc.app.data.local.HoldEntity
import com.mastoc.app.data.model.Climb
import com.mastoc.app.data.model.Face
import com.mastoc.app.data.model.Hold

// --- Climb Mappers ---

fun ClimbDto.toEntity(): ClimbEntity = ClimbEntity(
    id = id,
    stoktId = stoktId,
    faceId = faceId,
    setterId = setterId,
    setterName = setterName,
    name = name,
    holdsList = holdsList,
    gradeFont = gradeFont,
    gradeIrcra = gradeIrcra,
    feetRule = feetRule,
    description = description,
    isPrivate = isPrivate,
    climbedBy = climbedBy,
    totalLikes = totalLikes,
    source = source,
    personalNotes = personalNotes,
    isProject = isProject,
    createdAt = createdAt
)

fun ClimbEntity.toDomain(): Climb = Climb(
    id = id,
    stoktId = stoktId,
    faceId = faceId,
    setterId = setterId,
    setterName = setterName,
    name = name,
    holdsList = holdsList,
    gradeFont = gradeFont,
    gradeIrcra = gradeIrcra,
    feetRule = feetRule,
    description = description,
    isPrivate = isPrivate,
    climbedBy = climbedBy,
    totalLikes = totalLikes,
    source = source,
    personalNotes = personalNotes,
    isProject = isProject,
    createdAt = createdAt
)

fun ClimbDto.toDomain(): Climb = Climb(
    id = id,
    stoktId = stoktId,
    faceId = faceId,
    setterId = setterId,
    setterName = setterName,
    name = name,
    holdsList = holdsList,
    gradeFont = gradeFont,
    gradeIrcra = gradeIrcra,
    feetRule = feetRule,
    description = description,
    isPrivate = isPrivate,
    climbedBy = climbedBy,
    totalLikes = totalLikes,
    source = source,
    personalNotes = personalNotes,
    isProject = isProject,
    createdAt = createdAt
)

// --- Hold Mappers ---

fun HoldDto.toEntity(faceId: String): HoldEntity = HoldEntity(
    id = id,
    stoktId = stoktId,
    faceId = faceId,
    polygonStr = polygonStr,
    centroidX = centroidX,
    centroidY = centroidY,
    pathStr = pathStr,
    area = area,
    centerTapeStr = centerTapeStr,
    rightTapeStr = rightTapeStr,
    leftTapeStr = leftTapeStr
)

fun HoldEntity.toDomain(): Hold = Hold(
    id = id,
    stoktId = stoktId,
    faceId = faceId,
    polygonStr = polygonStr,
    centroidX = centroidX,
    centroidY = centroidY,
    pathStr = pathStr,
    area = area,
    centerTapeStr = centerTapeStr,
    rightTapeStr = rightTapeStr,
    leftTapeStr = leftTapeStr
)

fun HoldDto.toDomain(faceId: String): Hold = Hold(
    id = id,
    stoktId = stoktId,
    faceId = faceId,
    polygonStr = polygonStr,
    centroidX = centroidX,
    centroidY = centroidY,
    pathStr = pathStr,
    area = area,
    centerTapeStr = centerTapeStr,
    rightTapeStr = rightTapeStr,
    leftTapeStr = leftTapeStr
)

// --- Face Mappers ---

fun FaceDto.toEntity(): FaceEntity = FaceEntity(
    id = id,
    stoktId = stoktId,
    gymId = gymId,
    picturePath = picturePath,
    pictureWidth = pictureWidth,
    pictureHeight = pictureHeight,
    holdsCount = holdsCount,
    totalClimbs = climbsCount
)

fun FaceSetupDto.toEntity(): FaceEntity = FaceEntity(
    id = id,
    stoktId = stoktId,
    gymId = "", // Not available in setup response
    picturePath = picture?.name ?: "",
    pictureWidth = picture?.width,
    pictureHeight = picture?.height,
    holdsCount = holds.size,
    totalClimbs = totalClimbs,
    hasSymmetry = hasSymmetry,
    isActive = isActive
)

fun FaceEntity.toDomain(): Face = Face(
    id = id,
    stoktId = stoktId,
    gymId = gymId,
    picturePath = picturePath,
    pictureWidth = pictureWidth,
    pictureHeight = pictureHeight,
    holdsCount = holdsCount,
    totalClimbs = totalClimbs,
    hasSymmetry = hasSymmetry,
    isActive = isActive
)

fun FaceDto.toDomain(): Face = Face(
    id = id,
    stoktId = stoktId,
    gymId = gymId,
    picturePath = picturePath,
    pictureWidth = pictureWidth,
    pictureHeight = pictureHeight,
    holdsCount = holdsCount,
    totalClimbs = climbsCount
)
