package lessons.kt_08_07
class Student(var score: Int)
fun main() {
    val first = Student(80)
    val second = first
    second.score = 90
    println(first.score)
}
