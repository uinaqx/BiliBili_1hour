package lessons.kt_07_06
fun main() {
    val names = listOf("小林", "小陈")
    val name = names.getOrNull(5)
    println(name?.length ?: -1)
}
