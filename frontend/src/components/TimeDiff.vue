<template>
  <div>
    <p>{{ timeDifference }}</p>
  </div>
</template>

<script lang="ts">
import moment from 'moment';
import {defineComponent, computed} from "vue";

export default defineComponent({
  props: {
    dateTime: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    const timeDifference = computed(() => {
      const now = moment();
      const timestamp = moment(props.dateTime);
      const diffInSeconds = now.diff(timestamp, 'seconds');

      if (diffInSeconds < 60) {
        return `${diffInSeconds} Seconds ago`;
      } else if (diffInSeconds < 3600) {
        const diffInMinutes = Math.floor(diffInSeconds / 60);
        return `${diffInMinutes} A minute ago`;
      } else if (diffInSeconds < 86400) {
        const diffInHours = Math.floor(diffInSeconds / 3600);
        return `${diffInHours} Hours ago`;
      } else {
        const diffInDays = Math.floor(diffInSeconds / 86400);
        return `${diffInDays} Days ago`;
      }
    });
    console.log(timeDifference);

    return {
      timeDifference,
    };
  },
});
</script>
