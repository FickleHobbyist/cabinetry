SELECT width as Length,
    height AS Width,
    count(*) AS Qty,
    material_name AS Material,
    name as Label
FROM components
WHERE material_name LIKE "%PLY%"
GROUP BY material_name,
    name,
    width,
    height;