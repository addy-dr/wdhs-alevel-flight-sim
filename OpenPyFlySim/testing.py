import maths_module
import crash_handler

v1 = maths_module.Vector3([0.0, 0.0, 0.0])
v2 = maths_module.Vector3([1.0, 1.0, 1.0])
v3 = maths_module.Vector3([1.0, 2.0, 3.0])
v4 = maths_module.Vector3([2.0, 3.0, 4.0])
v5 = maths_module.Vector3([-1.0, -1.0, -1.0])
v6 = maths_module.Vector3([-2.0, -2.0, -2.0])

v7 = maths_module.Vector3([3.0, -3.0, 1.0])
v8 = maths_module.Vector3([4.0, 9.0, 2.0]) 
v9 = maths_module.Vector3([15.0, -2.0, 39.0]) 

v10 = maths_module.Vector3([1.0, 0.0, 0.0])
v11 = maths_module.Vector3([0.0, 0.0, 1.0])
v12 = maths_module.Vector3([0.0, -1.0, 0.0])
v13 = maths_module.Vector3([100.0, 0.0, 0.0])
v14 = maths_module.Vector3([-50.0, -50.0, -50.0])

def test_add():
    assert maths_module.Vector3.addVectors(v1,v1).val.all() == v1.val.all(), "Should be (0,0,0)"
    assert maths_module.Vector3.addVectors(v1,v2).val.all() == v2.val.all(), "Should be (1,1,1)"
    assert maths_module.Vector3.addVectors(v2,v3).val.all() == v4.val.all(), "Should be (2,3,4)"
    assert maths_module.Vector3.addVectors(v2,v5).val.all() == v1.val.all(), "Should be (0,0,0)"
    assert maths_module.Vector3.addVectors(v5,v5).val.all() == v6.val.all(), "Should be (-2,-2,-2)"

def test_sub():
    assert maths_module.Vector3.subtractVectors(v1,v1).val.all() == v1.val.all(), "Should be (0,0,0)"
    assert maths_module.Vector3.subtractVectors(v1,v2).val.all() == v5.val.all(), "Should be (-1,-1,-1)"
    assert maths_module.Vector3.subtractVectors(v1,v5).val.all() == v2.val.all(), "Should be (1,1,1)"
    assert maths_module.Vector3.subtractVectors(v2,v1).val.all() == v2.val.all(), "Should be (1,1,1)"
    assert maths_module.Vector3.subtractVectors(v4,v3).val.all() == v2.val.all(), "Should be (1,1,1)"

def test_dot():
    assert maths_module.Vector3.dot(v1,v1) == 0, "Should be 0"
    assert maths_module.Vector3.dot(v1,v2) == 0, "Should be 0"
    assert maths_module.Vector3.dot(v2,v2) == 3, "Should be 3"
    assert maths_module.Vector3.dot(v5,v5) == 3, "Should be 3"
    assert maths_module.Vector3.dot(v3,v5) == -6, "Should be -6"

def test_normalise():
    "also doubles to test magnitude"
    assert v1.normalise().val.all() == v1.val.all(), "Should be (0,0,0)"
    assert v2.normalise().val.all() == v2.val.all(), "Should be (1,1,1)"
    assert v13.normalise().val.all() == v10.val.all(), "Should be (1,0,0)"
    assert v14.normalise().val.all() == v5.val.all(), "Should be (-1,-1,-1)"

def test_cross():
    assert maths_module.Vector3.cross(v7,v8).val.all() == v9.val.all(), "Should be (15, -2, 39)"
    assert maths_module.Vector3.cross(v1,v1).val.all() == v1.val.all(), "Should be (0, 0, 0)"
    assert maths_module.Vector3.cross(v10,v11).val.all() == v12.val.all(), "Should be (0, -1, 0)"

def test_rotation():
    assert maths_module.rotate(v10,v12,90).val.all() == v11.val.all(), "Should be (0, 0, 1)"
    assert maths_module.rotate(v1,v12,360).val.all() == v1.val.all(), "Should be (0, 0, 0)"
    assert maths_module.rotate(v10,v12,-270).val.all() == v11.val.all(), "Should be (0, 0, 1)"

def test_get_data():
    "values as of last performing test"
    assert maths_module.getDatafileData("datacheckboxon") == "1", "Should be 1"
    assert maths_module.getDatafileData("host") == "12306", "Should be (0, 0, 0)"
    assert maths_module.getDatafileData("serverIP") == "192.168.1.46", "Should be (0, 0, 1)"

def test_get_data():
    "values as of last performing test"
    assert maths_module.getDatafileData("datacheckboxon") == "1", "Should be 1"
    assert maths_module.getDatafileData("host") == "12306", "Should be (0, 0, 0)"
    assert maths_module.getDatafileData("serverIP") == "192.168.1.46", "Should be (0, 0, 1)"

if __name__ == "__main__":
    test_add()
    print("Add test passed")
    test_sub()
    print("Subtraction test passed")
    test_dot()
    print("Dot Product test passed")
    test_cross()
    print("Cross Product test passed")
    test_normalise()
    print("Normalisation test passed")
    test_rotation()
    print("Rotation test passed")
    test_get_data()
    print("Data test passed")
    print("Everything passed")
