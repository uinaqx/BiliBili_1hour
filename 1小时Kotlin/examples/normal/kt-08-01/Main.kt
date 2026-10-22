package lessons.kt_08_01
class Student(val name: String, var score: Int)
fun main() {
    val student = Student("小林", 80)
    println(student.name)
    println(student.score)
}
