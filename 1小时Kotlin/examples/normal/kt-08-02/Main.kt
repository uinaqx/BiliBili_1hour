package lessons.kt_08_02
class Student(val name: String, var score: Int) {
    fun isPassed(): Boolean {
        return score >= 60
    }
}
fun main() {
    val student = Student("小林", 80)
    println(student.isPassed())
}
