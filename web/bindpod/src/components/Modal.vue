<template>
    <transition name="fade">
      <div class="modal" v-if="showModal">
        <div class="modal-dialog">
          <transition name="fade">
            <el-container>
              <el-header>{{ title }}</el-header>
              <span class="el-icon-close" @click="$emit('cancel')"></span>
              <el-main>
                <slot name="body"></slot>
              </el-main>
              <el-footer>
                <el-row>
                  <el-col>
                    <div class="btn_right">
                      <el-button size="medium" type="info" plain @click="$emit('cancel')">{{ cancelText }}</el-button>
                      <el-button size="medium" type="primary" plain @click="$emit('submit')" v-if="btnType">{{ sureText }}</el-button>
                    </div>
                  </el-col>
                </el-row>
              </el-footer>
            </el-container>
          </transition>
        </div>
      </div>
    </transition>
</template>

<script>
export default {
  name: "Modal",
  data() {
    return {
      show: true
    }
  },
  props: {
    btnType: {
      type: Boolean,
      default: true
    },
    title: String,
    sureText: {
      type: String,
      default: "确定"
    },
    cancelText: {
      type: String,
      default: "取消"
    },
    showModal: Boolean,
    }
}
</script>

<style scoped lang="scss">
.modal {
  &.fade-enter-active, &.fade-leave-active {
    transition: opacity 0.1s;
  }
  &.fade-enter, &.fade-leave-to /* .fade-leave-active below version 2.1.8 */ {
    opacity: 0;
  }
  z-index: 10;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: #00000036;

  .modal-dialog {
    border-radius: 3px;
    background-color: #FFFFFF;
    position: fixed;
    top: 10%;
    left: 50%;
    transform: translate(-50%, 10%);
    .el-icon-close {
      position: absolute;
      top: 15px;
      right: 15px;
      color: #afaaaa;
      &:hover {
        transform: scale(1.5);
      }
    }
    .el-header {
      border-bottom: 1px solid #eae4e4;
    }

    .el-footer {
      border-top: 1px solid #eae4e4;

      .btn_right {
        float: right;

        .el-button {
          text-align: center;
        }
      }

    }
  }
}
</style>
