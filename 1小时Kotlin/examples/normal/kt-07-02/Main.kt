package lessons.kt_07_02
fun main() {
    val nickname: String? = null
    val length = nickname?.length
    val display = nickname ?: "未填写"
    println(length)
    println(display)
}
