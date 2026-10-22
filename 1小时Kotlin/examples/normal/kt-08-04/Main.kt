package lessons.kt_08_04
data class Student(val name: String, val score: Int)
fun main() {
    val first = Student("小林", 80)
    val same = Student("小林", 80)
    println(first == same)
    println(first)
}
